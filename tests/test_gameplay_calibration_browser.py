"""Fixture-specific UI regression, NOT a general gameplay judge or model calibration.

All actions use normal keyboard/buttons; observations use rendered SVG/HUD and
screenshots. DOM-assisted reference checks are privileged to these authored
fixtures. They cannot establish accuracy on arbitrary canvas/3D games.
"""

from __future__ import annotations

import functools
import hashlib
import http.server
import json
import math
import os
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.browser,
    pytest.mark.skipif(
        os.environ.get("GAMEBENCH_GAMEPLAY_TESTS") != "1",
        reason="Run scripts/test-gameplay-calibration.sh in isolated Chromium",
    ),
]


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        instance = p.chromium.launch()
        yield instance
        instance.close()


@pytest.fixture(scope="module")
def origin():
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(QuietHandler, directory="/fixtures")
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.fixture(scope="module", autouse=True)
def summarize():
    yield
    results = [json.loads(path.read_text()) for path in Path("/output").glob("*/result.json")]
    valid = [
        r
        for r in results
        if r["observed_pass"] is not None and not r["page_errors"] and not r["execution_error"]
    ]
    summary = {
        "kind": "scripted_fixture_regression_not_agent_accuracy",
        "generated_at": datetime.now(UTC).isoformat(),
        "attempted_probes": len(results),
        "completed_probes": len(valid),
        "harness_errors": len(results) - len(valid),
        "expected_passes": sum(r["expected_pass"] for r in valid),
        "expected_faults": sum(not r["expected_pass"] for r in valid),
        "false_passes": sum(not r["expected_pass"] and r["observed_pass"] for r in valid),
        "false_failures": sum(r["expected_pass"] and not r["observed_pass"] for r in valid),
        "independent_agent_calibrated": False,
        "scope": "15 fixture-specific probes, not complete protocol criteria or UX scoring",
        "fixture_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in Path("/fixtures").iterdir()
            if path.is_file()
        },
        "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (Path("/output") / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


class Player:
    def __init__(self, page, directory, game):
        self.page = page
        self.directory = directory
        self.game = game
        self.events = []
        self.started = time.monotonic()

    def record(self, action, **kwargs):
        self.events.append(
            {"at_seconds": round(time.monotonic() - self.started, 3), "action": action, **kwargs}
        )

    def shot(self, label):
        filename = f"{len(self.events):03d}-{label}.png"
        self.page.screenshot(path=str(self.directory / filename))
        self.record("screenshot", file=filename, observation=self.observe())

    def observe(self):
        page = self.page
        # Only attributes of visible rendered shapes, never private JS/game state.
        if self.game == "platformer":
            sprite = page.locator("#player")
            location = [
                float(sprite.get_attribute("x")) + 13,
                float(sprite.get_attribute("y")) + 34,
            ]
        else:
            sprite = page.locator("#car")
            location = [float(sprite.get_attribute("cx")), float(sprite.get_attribute("cy"))]
        return {
            "state": page.locator("#state").inner_text(),
            "location": location,
            "counter": page.locator("#counter").inner_text(),
            "timer": page.locator("#timer").inner_text(),
            "speed": page.locator("#speed").inner_text(),
        }

    def hold(self, seconds, *keys):
        self.record("keys_down", keys=list(keys))
        try:
            for key in keys:
                self.page.keyboard.down(key)
            self.page.wait_for_timeout(seconds * 1000)
        finally:
            for key in keys:
                self.page.keyboard.up(key)
        self.record("keys_up", keys=list(keys), observation=self.observe())

    def wait(self, seconds):
        self.hold(seconds)

    def restart(self):
        self.page.get_by_role("button", name="Restart", exact=True).click()
        self.wait(0.05)
        self.record("restart", observation=self.observe())

    def x(self):
        return self.observe()["location"][0]

    def count(self):
        return int(self.observe()["counter"].split()[1])

    def go_to(self, target):
        # Feedback from the visible player avoids frame-rate-dependent key macros.
        deadline = time.monotonic() + 4
        while abs(self.x() - target) > 5 and time.monotonic() < deadline:
            self.hold(
                min(0.1, abs(self.x() - target) / 280),
                "ArrowRight" if self.x() < target else "ArrowLeft",
            )


def raised_platform(p):
    p.go_to(100)
    p.hold(0.50, "Space", "ArrowRight")
    p.wait(0.65)
    p.shot("landing")


def pit_loss(p):
    p.go_to(100)
    p.go_to(450)
    p.wait(0.7)
    p.shot("pit")


def reach_goal(p):
    p.go_to(100)
    p.go_to(345)
    p.hold(0.80, "Space", "ArrowRight")
    p.wait(0.3)
    p.go_to(945)
    p.wait(0.1)
    p.shot("goal")


def probe_platformer(p, criterion):
    if criterion == "movement":
        before = p.x()
        p.hold(0.25, "ArrowRight")
        right = p.x()
        p.hold(0.25, "ArrowLeft")
        return right > before + 35 and p.x() < right - 35
    if criterion in {"jump", "solid-platforms"}:
        raised_platform(p)
        landed = abs(p.observe()["location"][1] - 335) < 2
        p.wait(2.1)
        stable = abs(p.observe()["location"][1] - 335) < 2
        p.hold(0.2, "Space")
        rose = p.observe()["location"][1] < 300
        p.wait(0.9)
        return landed and stable and rose and abs(p.observe()["location"][1] - 335) < 2
    if criterion == "collectibles":
        p.go_to(100)
        first = p.count()
        p.go_to(50)
        p.go_to(100)
        revisit = p.count()
        raised_platform(p)
        second = p.count()
        p.wait(0.5)
        return first == 1 and revisit == 1 and second == 2 and p.count() == 2
    if criterion == "fall-loss":
        pit_loss(p)
        before = p.observe()
        p.hold(0.3, "ArrowRight", "Space")
        return before["state"] == "Lost" and before["location"] == p.observe()["location"]
    if criterion == "goal-win":
        if p.observe()["state"] != "Playing":
            return False
        reach_goal(p)
        return p.observe()["state"] == "Won" and p.x() >= 930
    if criterion in {"loss-restart", "win-restart"}:
        if criterion == "loss-restart":
            pit_loss(p)
            terminal = "Lost"
        else:
            reach_goal(p)
            terminal = "Won"
        reached = p.observe()["state"] == terminal and p.count() > 0
        p.restart()
        fresh = p.observe()["state"] == "Playing" and abs(p.x() - 50) < 3 and p.count() == 0
        p.go_to(100)
        return reached and fresh and p.count() == 1
    raise AssertionError(criterion)


def legal_lap(p):
    p.hold(11.5, "ArrowUp", "ArrowRight")
    p.shot("lap")


def probe_racing(p, criterion):
    if criterion == "acceleration":
        before = p.observe()["location"]
        p.hold(1.4, "ArrowUp")
        after = p.observe()["location"]
        return math.dist(before, after) > 12
    if criterion == "braking":
        p.hold(1.2, "ArrowUp")
        before = p.x()
        p.wait(0.6)
        coast_distance = p.x() - before
        p.restart()
        p.hold(1.2, "ArrowUp")
        before = p.x()
        p.hold(0.6, "ArrowDown")
        brake_distance = p.x() - before
        p.record("braking_comparison", coast_distance=coast_distance, brake_distance=brake_distance)
        return 0 < brake_distance < coast_distance * 0.75
    if criterion == "steering":
        p.hold(1.8, "ArrowUp", "ArrowRight")
        right_z = p.observe()["location"][1]
        p.restart()
        p.hold(1.8, "ArrowUp", "ArrowLeft")
        left_z = p.observe()["location"][1]
        return right_z > -57 and left_z < -63
    if criterion == "track-bounds":
        p.hold(4, "ArrowUp")
        outer = math.hypot(*p.observe()["location"])
        p.shot("outer-boundary")
        p.restart()
        # Move left of the start before turning inward; the previous straight-
        # then-right route met the outer wall first and never tested the inner one.
        p.hold(1.5, "ArrowDown")
        p.hold(1.4, "ArrowUp")
        radii = []
        for _ in range(35):
            p.hold(0.1, "ArrowUp", "ArrowRight")
            radii.append(math.hypot(*p.observe()["location"]))
        inner = min(radii)
        p.shot("inner-boundary")
        p.record("boundary_radii", outer=outer, inner=inner)
        # Requires both contacts, not merely remaining somewhere on the track.
        return 71 <= outer <= 72.1 and 47.9 <= inner <= 50
    if criterion == "ordered-checkpoints":
        p.hold(0.6, "ArrowDown", "ArrowRight")
        rejected = p.observe()["state"] == "Playing" and p.count() == 0
        p.hold(4.8, "ArrowDown", "ArrowRight")
        rejected = rejected and p.count() == 0 and p.observe()["state"] == "Playing"
        p.shot("invalid-order")
        p.restart()
        legal_lap(p)
        return rejected and p.count() == 3 and p.observe()["state"] == "Finished"
    if criterion == "lap-finish":
        legal_lap(p)
        before = p.observe()
        p.wait(3.1)
        return (
            before["state"] == "Finished"
            and p.count() == 3
            and before["timer"] == p.observe()["timer"]
            and float(before["timer"].split()[1]) > 0
        )
    if criterion == "restart":
        legal_lap(p)
        reached = p.observe()["state"] == "Finished" and p.count() == 3
        p.restart()
        fresh = (
            p.count() == 0
            and p.observe()["state"] == "Playing"
            and math.dist(p.observe()["location"], [0, -60]) < 1
            and float(p.observe()["timer"].split()[1]) < 0.5
        )
        p.hold(0.8, "ArrowUp")
        return reached and fresh and p.x() > 3
    raise AssertionError(criterion)


PROBES = [
    ("platformer", "movement", "frozen-player"),
    ("platformer", "jump", "cosmetic-jump"),
    ("platformer", "solid-platforms", "decorative-platform"),
    ("platformer", "collectibles", "duplicate-coin"),
    ("platformer", "fall-loss", "no-loss"),
    ("platformer", "goal-win", "premature-win"),
    ("platformer", "loss-restart", "stale-reset"),
    ("platformer", "win-restart", "stale-reset"),
    ("racing", "acceleration", "hud-only-speed"),
    ("racing", "braking", "no-brakes"),
    ("racing", "steering", "no-steering"),
    ("racing", "track-bounds", "no-boundaries"),
    ("racing", "ordered-checkpoints", "unordered-checkpoints"),
    ("racing", "lap-finish", "running-finish-clock"),
    ("racing", "restart", "stale-reset"),
]


@pytest.mark.parametrize("game,criterion,mutation", PROBES)
@pytest.mark.parametrize("broken", [False, True], ids=["reference", "mutation"])
def test_reference_probe(browser, origin, game, criterion, mutation, broken):
    variant = mutation if broken else "none"
    directory = Path("/output") / f"{game}-{criterion}-{variant}"
    directory.mkdir(parents=True)
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        reduced_motion="reduce",
        record_video_dir=str(directory),
        record_video_size={"width": 1280, "height": 800},
    )
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    p = Player(page, directory, game)
    observed = None
    execution_error = None
    try:
        page.goto(f"{origin}/?game={game}&defect={variant}")
        page.get_by_role("button", name="Start", exact=True).click()
        p.wait(0.1)
        p.shot("start")
        observed = (probe_platformer if game == "platformer" else probe_racing)(p, criterion)
        p.shot("end")
        assert not errors, errors
        assert observed is (not broken), p.events
        stage = page.locator("#stage").bounding_box()
        assert stage and stage["y"] + stage["height"] < 780
    except Exception as exc:
        if not isinstance(exc, AssertionError):
            execution_error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        context.close()  # Flush the motion evidence, including on an assertion failure.
        result = {
            "kind": "scripted_fixture_regression",
            "game": game,
            "criterion": criterion,
            "fixture_variant": variant,
            "expected_pass": not broken,
            "observed_pass": observed,
            "page_errors": errors,
            "events": p.events,
            "execution_error": execution_error,
            "independent_agent_calibrated": False,
            "browser": browser.version,
            "viewport": {"width": 1280, "height": 800},
            "source": "authored local fixture; visible DOM-assisted replay, non-blind",
        }
        (directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")


@pytest.mark.parametrize("game", ["platformer", "racing"])
def test_mobile_layout(browser, origin, game):
    directory = Path("/output") / f"{game}-mobile"
    directory.mkdir(parents=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})
    try:
        page.goto(f"{origin}/?game={game}")
        page.get_by_role("button", name="Start", exact=True).click()
        page.screenshot(path=str(directory / "mobile.png"))
        for selector in ["#stage", "#instructions", "#counter", "#restart"]:
            box = page.locator(selector).bounding_box()
            assert box and box["width"] > 0 and box["x"] >= 0
            assert box["x"] + box["width"] <= 390
            assert box["y"] + box["height"] <= 844
    finally:
        page.close()
