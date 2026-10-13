from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tomllib
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_frozen_calibration_bytes():
    manifest = json.loads((ROOT / "docs/migration-manifest.json").read_text())
    for item in manifest["files"]:
        if item["path"].startswith("datasets/"):
            assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_task_structure_and_harbor_parse():
    from harbor.models.task.task import Task

    for path in (ROOT / "datasets").glob("*/*/task.toml"):
        task = path.parent
        assert Task.is_valid_dir(task)
        Task(task)
        config = tomllib.loads(path.read_text())
        assert config["verifier"]["environment_mode"] == "separate"
        assert config["verifier"]["network_mode"] == "no-network"
        for filename in [
            "instruction.md",
            "environment/Dockerfile",
            "solution/solve.sh",
            "tests/test.sh",
            "tests/rubric.json",
            "tests/verify_submission.py",
        ]:
            assert (task / filename).is_file(), filename


def test_report_reference_metadata():
    entries = list((ROOT / "reports").glob("*/reference.json"))
    assert entries
    ids = set()
    for path in entries:
        entry = json.loads(path.read_text())
        assert set(entry) == {
            "schema_version",
            "kind",
            "id",
            "title",
            "date",
            "platforms",
            "report_url",
            "reproduced_by_public_checkout",
        }
        assert entry["schema_version"] == "0.1"
        assert entry["kind"] == "historical_reference"
        assert entry["id"] == path.parent.name and entry["id"] not in ids
        assert entry["title"] and entry["platforms"]
        date.fromisoformat(entry["date"])
        ids.add(entry["id"])
        assert entry["reproduced_by_public_checkout"] is False
        url = urlsplit(entry["report_url"])
        assert url.scheme == "https" and url.netloc == "aigamebench.com"
        assert url.path == f"/reports/{entry['id']}/report.html"
        assert not url.query and not url.fragment


def test_local_documentation_links():
    docs = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "GOVERNANCE.md",
        *ROOT.glob("docs/**/*.md"),
        *ROOT.glob("reports/**/*.md"),
        *ROOT.glob("platforms/**/*.md"),
    ]
    for document in docs:
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            assert (document.parent / target.split("#")[0]).exists(), (document, target)


def test_no_private_payload_paths_in_public_tree():
    # Narrow filename/size gate, NOT a claim of comprehensive secret detection.
    output = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT
    )
    for name in output.decode().split("\0"):
        if not name:
            continue
        path = Path(name)
        assert not ({"jobs", "artifacts", ".vercel", "node_modules", "web_home"} & set(path.parts))
        assert not path.name.startswith(".env") or path.name == ".env.example"
        assert path.name not in {"auth.json", "credentials.json", "Cookies", "Login Data"}
        assert not (ROOT / path).is_symlink()
        assert (ROOT / path).stat().st_size < 2 * 1024 * 1024


def test_ci_is_read_only_and_has_no_paid_or_deploy_lane():
    path = ROOT / ".github/workflows/checks.yml"
    workflow = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
    assert set(workflow["on"]) == {"pull_request", "push", "workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    assert set(workflow["jobs"]) == {"checks-and-package", "browser-calibration"}
    assert "secrets." not in path.read_text()
    for job in workflow["jobs"].values():
        assert job["runs-on"] == "ubuntu-24.04"
        for step in job["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"[^@]+@[a-f0-9]{40}", step["uses"])


def test_six_platform_references_are_explicitly_not_executable():
    from harbor.agents.factory import AgentFactory
    from harbor.models.agent.name import AgentName

    from ai_game_bench.cli import REFERENCE_PLATFORMS

    entries = list((ROOT / "platforms").glob("*/integration.json"))
    assert {path.parent.name for path in entries} == set(REFERENCE_PLATFORMS)
    assert len(entries) == 6
    for path in entries:
        entry = json.loads(path.read_text())
        assert entry["schema_version"] == "platform-reference/0.1"
        assert entry["id"] == path.parent.name
        assert entry["status"] == "reference_only"
        assert entry["public_execution_supported"] is False
        assert entry["setup"] and entry["artifact_handoff"] and entry["usage_sources"]
        assert (path.parent / "README.md").is_file()
        assert entry["report_ids"]
        for report_id in entry["report_ids"]:
            assert (ROOT / "reports" / report_id / "reference.json").is_file()
        if entry["historical_route"] == "local_cli":
            name = AgentName(entry["harbor_agent"])
            assert AgentFactory._AGENT_MAP[name] == entry["harbor_implementation"]
            assert entry["creation_entry_url"] is None
        else:
            assert entry["historical_route"] == "existing_profile_browser_ui"
            assert entry["harbor_agent"] is None and entry["harbor_implementation"] is None
            url = urlsplit(entry["creation_entry_url"])
            assert url.scheme == "https" and url.hostname
            assert not url.username and not url.password and not url.query and not url.fragment


def test_shared_observation_template_is_not_a_run_or_score():
    record = json.loads((ROOT / "platforms/shared/record.example.json").read_text())
    assert record["record_status"] == "blank_template_not_a_result"
    assert record["creation"]["status"] == "not_started"
    assert record["artifact"]["game_url"] is None
    assert record["artifact"]["frozen"] is False
    assert record["cost"]["actual_run_charge"]["amount"] is None
    assert record["public_release_approved"] is False
    assert record["training_eligible"] is False
