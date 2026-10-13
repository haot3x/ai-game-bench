# Security and data handling

Treat generated games, task Dockerfiles, platform output and PR code as untrusted.
Use isolated disposable runtimes; do not mount personal home directories, Chrome
profiles, credentials or Docker sockets into a game/verifier container.

Do not report secrets publicly. Use GitHub's private vulnerability reporting when
enabled; otherwise contact a Mopan maintainer privately to arrange a safe channel.
Do not include exploit details or private evidence in a public issue.

Raw jobs and browser evidence are private by default, even if the game URL is
public. Before sharing: remove credentials, account identifiers, signed URLs,
irrelevant conversations and third-party content without redistribution rights.
Evidence redaction must retain a record of what is missing; it must not change a
verdict invisibly. A private repository is not a safe place for API keys either.

Public PR workflows have no model/deployment secrets and do not execute on
personal self-hosted runners. They test proposed code but are not an independent
security or scientific certification. Maintainers must inspect workflow and
checker changes, not accept a green result from a PR that disabled its own test.
