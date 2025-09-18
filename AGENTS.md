# Repository Guidelines

## Project Structure & Module Organization
- Root project lives in `trader/` (Poetry-managed Python 3.10).
- Core code: `packages/valory/skills/*` (each skill is an FSM-based component).
- Service configs: `packages/valory/services/trader/` (e.g., `service.yaml`).
- Tests colocated per skill: `packages/valory/skills/<skill>/tests/`.
- Utilities and tooling: `scripts/`, `pyinstaller/`, `mints/`, `img/`.

## Build, Test, and Development Commands
- Setup env: `cd trader && poetry install && poetry shell`.
- Format/lint/security + generators/checks: `make all-checks`.
- Run tests for all key skills (Linux, Python 3.10): `tox -e py3.10-linux`.
- Quick test for one skill: `pytest packages/valory/skills/trader_abci/tests -q`.
- Build agent runner binary: `make build-agent-runner` (or `build-agent-runner-mac`).
- Service run/deploy: follow `README.md` (e.g., `autonomy init`, `autonomy build-image`, `autonomy deploy run`).

## Coding Style & Naming Conventions
- Python: 4-space indent, Black formatting (line length 88, enforced via `make format`).
- Imports: isort settings compatible with Black.
- Typing: mypy configured (see `tox.ini`); add/maintain type hints.
- Docs: Sphinx-style docstrings (darglint enforces basic rules).
- Naming: modules/files `snake_case.py`, functions/vars `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.

## Testing Guidelines
- Framework: pytest with markers `integration` and `e2e` (see `tox.ini`).
- Location: place tests under the corresponding skill’s `tests/` folder.
- Naming: files `test_*.py`; prefer small, focused tests; add fixtures in `conftest.py` when reusable.
- Commands: run locally with `pytest …` or via `tox -e py3.10-linux`. Keep/raise coverage where practical.

## Commit & Pull Request Guidelines
- Commits follow Conventional Commits where possible: `feat:`, `fix:`, `chore:`, `refactor:`, etc. Use imperative mood and a concise subject.
- PRs must include: purpose/summary, clear checklist of changes, any config migrations, and links to related issues.
- Before opening a PR: run `make all-checks` and relevant `tox` envs; include test plan (commands + results). Attach logs for runtime-affecting changes.

## Security & Configuration Tips
- Do not commit secrets. Run `make security` (Bandit, Safety, Gitleaks) before PRs.
- Configuration is primarily via env vars and `packages/valory/services/trader/service.yaml`. Update docs when changing config surface.

