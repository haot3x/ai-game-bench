"""Offline fixture metadata/coverage tests; they make no gameplay claims."""

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures/calibration/gameplay-v1"
METHODS = {"platformer": "platformer-browser-pilot-v1", "racing": "racing-3d-browser-pilot-v1"}


def test_case_catalog_matches_browser_probe_inventory():
    cases = json.loads((FIXTURES / "cases.json").read_text())
    tree = ast.parse((ROOT / "tests/test_gameplay_calibration_browser.py").read_text())
    inventory = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "PROBES" for t in node.targets)
    )
    assert inventory == [(p["game"], p["criterion"], p["mutation"]) for p in cases["pairs"]]
    assert len(inventory) == 15 and len(set(inventory)) == 15
    assert cases["kind"] == "fixture_regression_not_agent_calibration"
    assert cases["gameplay_score"] is None
    source = (FIXTURES / "game.js").read_text()
    for _, _, mutation in inventory:
        assert f"'{mutation}'" in source


def test_every_criterion_has_an_acceptance_card_and_declared_coverage():
    cases = json.loads((FIXTURES / "cases.json").read_text())
    for game, method in METHODS.items():
        protocol = ROOT / "protocols" / method
        rubric = json.loads((protocol / "rubric.json").read_text())
        criteria = {c["id"] for c in rubric["criteria"]}
        automated = {p["criterion"] for p in cases["pairs"] if p["game"] == game}
        manual = set(cases["manual_only"][game])
        assert not automated & manual
        assert automated | manual | {"delivery-time"} == criteria
        card = (protocol / "acceptance.md").read_text()
        for criterion in rubric["criteria"]:
            if not criterion["allow_partial"]:
                assert f"| {criterion['id']} |" in card
        assert "not_tested" in card and "infrastructure" in card
        assert "historical" in card.lower()


def test_fixture_document_links_and_isolated_ci_entry():
    for target in re.findall(r"\]\(([^)]+)\)", (FIXTURES / "README.md").read_text()):
        if "://" not in target:
            assert (FIXTURES / target.split("#")[0]).exists()
    script = (ROOT / "scripts/test-gameplay-calibration.sh").read_text()
    assert "--network none --read-only" in script
    assert "mktemp -d" in script and "artifacts/gameplay-calibration" in script
    assert "test-gameplay-calibration.sh" in (ROOT / ".github/workflows/checks.yml").read_text()
    assert "--privileged" not in script and "docker.sock" not in script
