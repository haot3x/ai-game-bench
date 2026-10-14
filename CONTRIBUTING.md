# Contributing

Use your own authorized accounts. Apply the same rules to every platform,
including Mopan. Only designated Mopan maintainers merge.

- **Result:** follow [the submission guide](docs/submissions.md), publish one
  evidence-package PR. No prior Discussion or private workspace is required.
- **Task / policy / eval:** follow [adding tasks](docs/adding-tasks.md). An
  [Ideas proposal](https://github.com/mopan-ai/ai-game-bench/discussions/categories/ideas)
  is useful for large changes, but a scoped PR is also welcome.
- **Platform:** follow [the integration contract](docs/platforms.md), include
  free mocked tests before an authorized real run.
- **Verifier fix:** provide a minimal wrong verdict and regression test.
  Changed scoring meaning requires a new version.

Run `./verify.sh`. Runtime changes also need the free browser and Harbor smoke
checks. State exactly what ran, limitations and AI assistance in the PR.

Read the [public-data terms](README.md#public-data-and-privacy-terms) **before
pushing to your fork**. Submit only licensed, task-scoped, reviewed exports.
Include every attempt, missing evidence, affiliation and known limitations.
Corrections add a new submission revision; do not overwrite accepted records.

Maintainers use [the review checklist](docs/reviewing-submissions.md). A valid
package with a failed game is useful data; an impressive game with unsupported
claims is not a verified result. CI, acceptance, independent reproduction and
website publication are separate.

Maintainer-funded reruns require separate approval of task, revision, platform,
attempts, time and spending. No model execution is triggered by posting a proposal.
See [governance](GOVERNANCE.md) and [Actions](docs/contribution-workflow.md).
