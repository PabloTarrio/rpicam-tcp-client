# Contributing Guide

Thank you for your interest in contributing to **rpicam-tcp-client**!
This document explains how to set up the project locally and submit changes.

---

## Requirements

- Python 3.10+
- Git

---

## Local Setup

1. Fork the repository and clone your fork:
    ```bash
    git clone https://github.com/<your-username>/rpicam-tcp-client.git
    cd rpicam-tcp-client
    ```

2. Install the project in development mode:
    ```bash
    pip install -e ".[dev]"
    ```

3. Verify everything works:
    ```bash
    pytest
    ruff check .
    ```

## Branching Strategy

Use descriptive branch names following this convention:

| Prefix | Use case           | Example                 |
| ------ | ------------------ | ----------------------- |
| feat/  | New feature        | feat/add-rotation-param |
| fix/   | Bug fix            | fix/correct-bgr-colors  |
| docs/  | Documentation only | docs/update-readme      |
| test/  | Tests only         | test/add-client-tests   |
| ci/    | CI/CD changes      | ci/add-coverage-report  |

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standards:

```text
feat: add rotation parameter to CameraClient
fix: correct RGB to BGR conversion in get_frame
docs: update examples README with screenshots
test: add unit tests for CameraClient
```

## Pull Requests

1. Open a PR against the `main` branch
2. Make sure all CI checks pass (lint + tests)
3. Write a clear description of what the PR does and why

## Code Style

This project uses `ruff` for linting and formatting. Before commiting, run:

```bash
ruff check .
ruff format .
```

CI will reject any PR that does not pass these checks.

## Running Test

```bash
pytest          # run all tests
pytest --cov    # run with coverage report
```

## Questions

Open an [issue](https://github.com/PabloTarrio/rpicam-tcp-client/issues) if you have any questions or suggestions.