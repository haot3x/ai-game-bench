# Contributing

Start with one scoped PR. No invitation or prior Discussion is required.

- **Result:** follow [the submission guide](docs/submissions.md) to record,
  package and submit your evidence. Failed games are useful data too.
- **Task / policy / eval:** follow [adding tasks](docs/adding-tasks.md).
  Discuss large changes in [Ideas](https://github.com/mopan-ai/ai-game-bench/discussions/categories/ideas);
  small scoped PRs are welcome directly.
- **Platform:** follow [the integration contract](docs/platforms.md), with free
  mocked tests before an authorized real run.
- **Verifier fix:** include a minimal wrong verdict and regression test.
  Changing scoring meaning requires a new version.

Use your own authorized accounts. Before pushing, read the
[public-data terms](README.md#public-data-and-privacy-terms): submit only reviewed,
task-scoped material you have permission to share. Include all attempts, evidence
gaps, affiliation and AI assistance. Keep credentials and raw jobs local.

Run `./verify.sh`; runtime changes also need the free browser and Harbor smoke
checks. State what ran and any limitations. Correct accepted results with a new
revision, never by overwriting their records.

Mopan maintainers review and merge; passing CI is not evidence approval or
automatic website publication. Proposals do not trigger paid runs.
[Review process](docs/contribution-workflow.md) · [Governance](GOVERNANCE.md)
