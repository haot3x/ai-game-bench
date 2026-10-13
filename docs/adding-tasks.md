# Contribute a task

A task needs a testable contract, not only an attractive prompt. First open a task
proposal describing the game type, capability covered and how it will be checked.
For v0, favor small deterministic mechanics and authored, redistributable assets.

Use the counter as a packaging example, not a universal gameplay rubric:

```text
datasets/<dataset-version>/<task-id>/
  instruction.md
  task.toml
  environment/Dockerfile
  solution/solve.sh
  solution/files/...
  tests/Dockerfile
  tests/test.sh
  tests/rubric.json
  tests/verify_submission.py
```

Submit these files plus tests, asset licensing/provenance and a short explanation
of limitations. Keep secret checks and gold answers out of creator instructions.
The legacy `MOPAN_PROMPT_START/END` markers in the counter identify its original
product prompt; they are preserved for identity, not permission to call Mopan.

Acceptance:

1. Harbor can parse the task; environments build on the supported platform.
2. Oracle passes; Nop fails without an infrastructure exception.
3. Deliberately broken fixtures fail for the right reason. Include a false-pass
   trap, not only the happy path.
4. Evidence explains every verdict. Browser/setup errors remain exceptions.
5. Replaying a frozen local artifact gives the same deterministic result.
6. No unlicensed assets, credentials or external paid calls in default checks.

Run `./verify.sh`, browser checks and native Harbor trials locally. For a new
task, use `agb run --task <dataset-version>/<task-id> --agent oracle` and Nop.
CI currently builds/tests the counter; it **does not automatically exercise every
new task**. A task PR must add its free calibration to CI or explain the reviewed
manual gate. Never claim file validation alone verified a game.

Released task files are immutable. For prompt, rubric or verifier changes, add a
new task/dataset version and describe the compatibility break. Regression tests
and new defect fixtures are welcome; do not relabel historical results.
