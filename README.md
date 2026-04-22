# Social Network Kata

A small, Docker-packaged social-network backend built test-first with strict
TDD discipline. The kata spans three bounded contexts — **Users**, **Posts /
Timeline**, and **Messaging** — and is intentionally minimal: in-memory
repositories, no web framework, no real database. The value is in the process
(requirements → architecture → RED-GREEN-REFACTOR → CI/CD → docs), not in the
line count.

This repository is the coursework for the **SDP — Powered by AI Agents**
course at the University of Novi Sad.

## What the kata solves

Every user-facing feature is captured as a bundle (user story + supporting
INFRA / BE / FE stories) with GIVEN-WHEN-THEN scenarios. Each scenario becomes
one test; each test drives one minimal implementation commit. The git log is
the primary artefact — it shows the incremental progression from empty repo
to working feature.

## Tech stack

| Concern | Choice |
| --- | --- |
| Language / runtime | Python 3.12 |
| Testing | pytest |
| Packaging / execution | Docker (`python:3.12-slim`) |
| CI | GitHub Actions (tests on every push) |
| Docs | Sphinx + MyST parser, deployed to GitHub Pages |
| Architecture method | arc42 + C4 diagrams (PlantUML) |
| Pre-commit hooks | black, isort, ruff, bandit, detect-secrets, docker-test |

## Architecture overview

Three bounded contexts communicate over clear interfaces and own their own
data:

- **Users Service** — registration, login, profile, follow graph
- **Posts Service** — create post, aggregated timeline feed
- **Messaging Service** — direct messages between users

The deployment topology is Docker containers behind an nginx reverse proxy.
Full detail lives in the [arc42 documentation](https://github.com/Ivanovic0245/sdp-powered-by-ai-agents-aleksandar-ivanovic/tree/master/docs/architecture)
— see chapter 5 (Building Block View) and chapter 7 (Deployment View) first.

## Build and run

All commands assume Docker is available on the host.

```bash
# Build the image
docker build -t social-network-kata .

# Run the test suite inside the container
docker run --rm social-network-kata
```

The default container command is `pytest tests/ -v`, so a successful
`docker run` is also the functional smoke test for the kata.

## Run tests locally (without Docker)

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Project structure

```
.
├── Dockerfile                  # Runtime image; CMD runs the test suite
├── requirements.txt            # Runtime + test dependencies
├── src/
│   ├── users/                  # Users bounded context
│   └── posts/                  # Posts / Timeline bounded context
├── tests/
│   ├── users/                  # User registration and login scenarios
│   └── posts/                  # Post creation and timeline scenarios
├── docs/
│   ├── architecture/           # arc42 chapters 1–12
│   ├── user-stories/           # Story bundles per bounded context
│   ├── conf.py                 # Sphinx configuration
│   └── index.rst               # Documentation entry point
├── .github/workflows/          # CI (tests) and docs-deploy pipelines
├── .kiro/agents/               # Agent configurations used during the course
└── scripts/hooks/              # Pre-commit hook implementations
```

## Documentation

The Sphinx site is published to GitHub Pages and covers the full arc42
architecture plus every user-story bundle with GIVEN-WHEN-THEN scenarios.

> **Live site:** https://ivanovic0245.github.io/sdp-powered-by-ai-agents-aleksandar-ivanovic/

To build the docs locally:

```bash
pip install -r docs/requirements.txt
cd docs && make html
# Open docs/_build/html/index.html
```

## License

Released under the [MIT License](https://github.com/Ivanovic0245/sdp-powered-by-ai-agents-aleksandar-ivanovic/blob/master/LICENSE).

## Author

**Aleksandar Ivanović** — student, SDP — Powered by AI Agents, University of
Novi Sad, 2026.
