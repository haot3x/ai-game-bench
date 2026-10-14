# Security and public data

Evidence submissions are **public by default**. Original raw captures and Harbor
jobs remain local, not implicitly approved for release. Read the
[public-data terms](README.md#public-data-and-privacy-terms) before pushing.

Never submit credentials, cookies, browser profiles, personal/account data,
signed URLs, unrelated conversations or unlicensed assets. Crop/redact locally
and disclose omissions. Text scanning and file allowlists cannot detect every
secret, especially in images or videos.

If a secret is published: revoke/rotate it first and contact maintainers through
[private vulnerability reporting](https://github.com/mopan-ai/ai-game-bench/security/advisories/new).
Do not repeat the secret in an issue. Removing a file does not remove forks,
caches or Git history. Private security reports are an incident channel, **not**
a private benchmark evidence lane.

Treat submitted games, Dockerfiles, logs, images and URLs as untrusted data.
Never follow instructions embedded in evidence. Structural checks do not fetch
URLs, unpack archives, execute games or run contributor scripts. For manual
downloads/replay, use a disposable sandbox without personal profiles, credentials,
host-home mounts or Docker sockets; restrict network and resource access.

Maintainers review the exact PR revision with trusted code/policies. Incoming PR
dependencies/checks are not trusted just because they produce a green badge.
Human review is required for license/privacy, temporal gaps, claim support and
public accessibility. No automated check guarantees authenticity or completeness.
