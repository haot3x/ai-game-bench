# Contributing

Contributions are welcome from people building, evaluating or playing AI-created
games. Mopan maintainers review and merge the initial release. Contributor
affiliation does not determine acceptance; apply the same criteria to Mopan.

## Choose a contribution

| Contribution | Include | Review gate |
| --- | --- | --- |
| Task | Harbor package, rubric, reference solution, negative fixtures, license | Free calibration + method review |
| Platform | Harbor integration/config, setup guide, mocked lifecycle tests | Contract checks + authorized real smoke |
| Result/report | Method, exact versions, attempts, evidence references, limitations | Data/privacy review; reproduction is separate |
| Verifier fix | Minimal wrong verdict, expected behavior, regression test | No score inflation; new version when meaning changes |
| Documentation | Reproducible clarification/example | Link and technical review |

For a new task, platform or scoring change, open a proposal issue before a large
PR. Small fixes may go directly to PR. See [task requirements](docs/adding-tasks.md)
and [platform contract](docs/platforms.md).
Use the existing [platform directories](platforms/README.md) as reference layouts
for a new platform; provide a method and evidence, not only a name or model price.

## Local checks and PR

1. Fork, create a branch and install with `uv sync --locked`.
2. Run `./verify.sh`. Runtime changes also need `./scripts/test-browser.sh` and
   `./scripts/run-smoke.sh` (both free of model usage).
3. Describe the change, commands actually run, remaining gaps and AI assistance.
   You are responsible for understanding and validating contributed code.
4. Include a scrubbed summary, never raw `jobs/`, login state or private assets.
5. Wait for Mopan maintainer review. Passing CI alone does not authorize merge,
   official scores, model spending or website publication.

Contributors use their own authorized accounts for real runs. Do not request
shared credentials. A maintainer-funded rerun needs a separately approved task,
model/platform, revision, attempt count and cost cap.

## Evidence and privacy

Use the existing [reports](reports/README.md) as disclosure examples, not as a
universal scoring rubric. Submitter-reported, maintainer-reviewed and independently
reproduced are different statuses. Preserve all attempts and explain missing
evidence; do not select only the best run or silently revise old scores.

If evidence cannot be shared publicly, request a private review workspace in
the proposal. Do not paste it into a public issue first. Automatic private
workspace provisioning is a **proposal**, not an available service yet.
Never upload passwords, cookies, API keys or an entire personal agent session.
Share only task-scoped, scrubbed evidence with explicit publication rights.

See [the exact trigger/build/review matrix](docs/contribution-workflow.md).
