from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ai_game_bench import cli

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def native_job(tmp_path):
    # Authored minimal native Harbor records, never copied from private runs.
    from harbor.models.job.result import JobResult, JobStats
    from harbor.models.trial.result import TrialResult

    trial = TrialResult.model_validate(
        {
            "task_name": "synthetic-test",
            "trial_name": "trial-1",
            "trial_uri": "file:///synthetic/trial-1",
            "task_id": {"path": "datasets/synthetic/task"},
            "task_checksum": "0" * 64,
            "config": {"task": {"path": "datasets/synthetic/task"}},
            "agent_info": {"name": "oracle", "version": "1.0"},
            "verifier_result": {"rewards": {"overall": 1}},
            "started_at": "2026-01-01T00:00:00Z",
            "finished_at": "2026-01-01T00:01:00Z",
        }
    )
    job = JobResult.model_validate(
        {
            "id": "00000000-0000-4000-8000-000000000001",
            "started_at": "2026-01-01T00:00:00Z",
            "finished_at": "2026-01-01T00:01:00Z",
            "n_total_trials": 1,
            "stats": JobStats.from_trial_results([trial]),
        }
    )
    (tmp_path / "trial-1").mkdir()
    (tmp_path / "result.json").write_text(job.model_dump_json())
    (tmp_path / "trial-1/result.json").write_text(trial.model_dump_json())
    return tmp_path


def change_record(path, transform):
    record = json.loads(path.read_text())
    transform(record)
    path.write_text(json.dumps(record))


def test_checkout_discovery(monkeypatch):
    monkeypatch.chdir(ROOT / "tests")
    assert cli.repository_root() == ROOT


def test_missing_checkout(tmp_path):
    with pytest.raises(ValueError, match="checkout"):
        cli.repository_root(tmp_path)


def test_default_task():
    assert cli.task_directory(ROOT, cli.DEFAULT_TASK).is_dir()


@pytest.mark.parametrize("task", ["../README.md", "/tmp", "missing/task"])
def test_invalid_task(task):
    with pytest.raises(ValueError, match="Task must"):
        cli.task_directory(ROOT, task)


@pytest.mark.parametrize("agent", cli.REFERENCE_PLATFORMS)
def test_unintegrated_agents_cannot_silently_run(agent, monkeypatch):
    def forbidden():
        pytest.fail("Should refuse unsupported creator before resolving Harbor")

    monkeypatch.setattr(cli, "harbor_executable", forbidden)
    with pytest.raises(ValueError, match="not integrated"):
        cli.run_command(ROOT, cli.DEFAULT_TASK, agent, "new-job")


@pytest.mark.parametrize("name", ["../escape", "a/b", "-flag", "x; touch x", "", "a" * 81])
def test_unsafe_job_name(name):
    with pytest.raises(ValueError, match="Job name"):
        cli.run_command(ROOT, cli.DEFAULT_TASK, "oracle", name)


def test_existing_job_not_overwritten(tmp_path):
    (tmp_path / "jobs/existing").mkdir(parents=True)
    with pytest.raises(ValueError, match="already exists"):
        cli.run_command(tmp_path, cli.DEFAULT_TASK, "oracle", "existing")


def test_run_is_thin_native_harbor_command(monkeypatch):
    monkeypatch.setattr(cli, "harbor_executable", lambda: "/venv/bin/harbor")
    command = cli.run_command(ROOT, cli.DEFAULT_TASK, "nop", "new-job")
    assert command[:2] == ["/venv/bin/harbor", "run"]
    assert command[command.index("-a") + 1] == "nop"
    assert command[command.index("--max-retries") + 1] == "0"
    assert command[command.index("--n-attempts") + 1] == "1"
    assert command[command.index("--n-concurrent") + 1] == "1"
    assert command[command.index("--jobs-dir") + 1] == str(ROOT / "jobs")


def test_dry_run_never_launches(monkeypatch, capsys):
    monkeypatch.setattr(cli, "harbor_executable", lambda: "/venv/bin/harbor")
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("launched"))
    assert cli.main(["--repo", str(ROOT), "run", "--dry-run"]) == 0
    assert "HARBOR_TELEMETRY=0" in capsys.readouterr().out


def test_inspect_completed(native_job):
    assert cli.inspect_job(native_job, 1)["trials"][0]["rewards"] == {"overall": 1}


def test_zero_is_a_valid_scored_result(native_job):
    change_record(
        native_job / "trial-1/result.json",
        lambda r: r["verifier_result"].update(rewards={"overall": 0}),
    )
    assert cli.inspect_job(native_job, 0)["infrastructure_errors"] == 0
    with pytest.raises(ValueError, match="Expected overall"):
        cli.inspect_job(native_job, 1)


@pytest.mark.parametrize(
    "field,value",
    [
        ("n_errored_trials", 1),
        ("n_completed_trials", 0),
        ("n_pending_trials", 1),
        ("n_cancelled_trials", 1),
        ("n_running_trials", 1),
    ],
)
def test_job_errors_or_incomplete_are_not_zero(native_job, field, value):
    change_record(native_job / "result.json", lambda r: r["stats"].update({field: value}))
    with pytest.raises(ValueError, match="incomplete|infrastructure"):
        cli.inspect_job(native_job)


@pytest.mark.parametrize(
    "value", [None, {"rewards": None}, {"rewards": {}}, {"rewards": {"overall": float("nan")}}]
)
def test_missing_or_invalid_reward_rejected(native_job, value):
    change_record(native_job / "trial-1/result.json", lambda r: r.update(verifier_result=value))
    with pytest.raises(ValueError, match="missing|invalid"):
        cli.inspect_job(native_job)


def test_missing_trial_rejected(native_job):
    (native_job / "trial-1/result.json").unlink()
    with pytest.raises(ValueError, match="every completed"):
        cli.inspect_job(native_job)


def test_trial_exception_not_hidden_by_job_summary(native_job):
    change_record(
        native_job / "trial-1/result.json",
        lambda r: r.update(
            exception_info={
                "exception_type": "SyntheticInfrastructureError",
                "exception_message": "broken browser",
                "exception_traceback": "synthetic",
                "occurred_at": "2026-01-01T00:01:00Z",
            }
        ),
    )
    with pytest.raises(ValueError, match="infrastructure"):
        cli.inspect_job(native_job)


def test_view_uses_native_localhost(monkeypatch):
    monkeypatch.setattr(cli, "harbor_executable", lambda: "/venv/bin/harbor")
    calls = []

    def capture(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", capture)
    assert cli.main(["--repo", str(ROOT), "view"]) == 0
    command, kwargs = calls[0]
    assert command == [
        "/venv/bin/harbor",
        "view",
        str(ROOT / "jobs"),
        "--host",
        "127.0.0.1",
        "--port",
        "8080",
    ]
    assert kwargs["env"]["HARBOR_TELEMETRY"] == "0"


@pytest.mark.parametrize("platform", cli.REFERENCE_PLATFORMS)
def test_platform_reference_is_read_only(platform, monkeypatch, capsys):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("launched"))
    assert cli.main(["--repo", str(ROOT), "platforms", platform, "--json"]) == 0
    record = json.loads(capsys.readouterr().out)
    assert record["id"] == platform
    assert record["public_execution_supported"] is False
    assert cli.main(["--repo", str(ROOT), "platforms", platform]) == 0
    assert (
        capsys.readouterr().out == (ROOT / "platforms" / platform / "README.md").read_text() + "\n"
    )


def test_platform_listing_includes_manus(capsys):
    assert cli.main(["platforms"]) == 0
    assert "manus" in capsys.readouterr().out


def test_platform_json_requires_a_name(capsys):
    assert cli.main(["platforms", "--json"]) == 2
    assert "Choose a platform" in capsys.readouterr().err


def test_unknown_platform_does_not_read_arbitrary_paths():
    with pytest.raises(SystemExit) as exc:
        cli.main(["platforms", "../../private"])
    assert exc.value.code == 2
