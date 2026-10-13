# Reports and evidence submissions

The presentation site owns HTML, charts and public game demos. This repository
initially contains only reviewed-site **references**, not copied historical jobs
or newly verified claims. Some report pages may require site access. These links
do not guarantee anonymous access or independent reproducibility.

| Report | Scope |
| --- | --- |
| [001](https://aigamebench.com/reports/001-tetris-five-platform/report.html) | One Tetris task across five platforms |
| [002](https://aigamebench.com/reports/002-codex-gpt-6-sol-astra-tetris/report.html) | Two Codex model configurations |
| [003](https://aigamebench.com/reports/003-manus-six-platform-tetris/report.html) | Six-platform Tetris comparison |
| [004](https://aigamebench.com/reports/004-mopan-astra-gemini-tetris/report.html) | Two Mopan main-agent models |

Each reference has its own directory and `reference.json`. The initial catalog
contains no scores to silently reinterpret, normalize or rerank. Historical
results were not regenerated using the public counter task.

## New result contribution

Open a result proposal with:

- Task/prompt version and hash; evaluation policy/rubric version.
- Creator platform, harness/version, model and effort (unknown when not exposed).
- All attempts, settings, follow-ups, start/end times and runtime conditions.
- Game URL/build version or frozen artifact hash; observation time and access limits.
- Per-criterion outcomes with evidence references; infrastructure failures apart
  from scored failures; evaluator identity and review mode.
- Duration, measured usage, model-cost estimate, credit valuation and actual
  payment as separate fields with source/currency/date. Unknown is not zero.
- Rights/privacy review, limitations and self-reported/reviewed/reproduced status.

Initially a maintainer reviews the proposal and arranges private evidence sharing
if necessary. Full submission packaging and HTML preview automation are planned,
not existing CLI commands. Do not submit a raw Harbor job to this public repo.

Publication creates a sanitized, explicit export and a separate landing-site PR.
It never makes a private evidence repository public or copies its Git history.
