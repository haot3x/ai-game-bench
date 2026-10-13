# DOM interaction calibration fixtures

Authored in this repository for `smoke-create-v0.2`, under the repository's
Apache-2.0 license. No production game, external artwork, prompt snapshot, or
user content is included. The positive fixture intentionally differs from the
Oracle implementation. Each negative fixture has one deliberately broken rule.

`scripts/test-browser.sh` evaluates each HTML file with real Chromium, inside a
network-disabled disposable container. The external-resource and navigation URLs
are deliberately non-resolving and blocked before any network request leaves.

Fixture bytes are versioned in Git; each evaluated copy has its SHA-256 recorded
in `details.json`. Generated screenshots/traces stay outside Git. These fixtures
test known failure modes, not resistance to arbitrary adversarial submissions.
