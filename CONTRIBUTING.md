# Contributing

## Getting started

1. Fork the repository.
2. Follow the [Development Guide](DEVELOPMENT.md) to set up a local
   environment.
3. Create a branch: `git checkout -b feat/my-change`.

## Before you open a PR

- [ ] Backend change? Add/extend unit tests under `tests/unit/` and run
      `python -m pytest tests/ -q` (all green).
- [ ] Frontend change? `node --check` every touched page script; pages and
      scripts must serve at `/tools/{id}` and `/static/assets/js/pages/{id}.js`.
- [ ] New tool? Add the registry entry in `app/core/capabilities.py` (the
      test suite asserts the total count) and a page under
      `frontend/pages/` following the `tool-kit.js` bootstrap pattern.
- [ ] No secrets, tokens, or absolute paths committed.
- [ ] Update the relevant doc file if behavior changed (`README.md`,
      `ARCHITECTURE.md`, `DEPLOYMENT.md`, `SECURITY.md`).

## Code style

- Python 3.10+, no formatting tool mandated — match surrounding code.
- Layer discipline: controllers call services, services call adapters;
  no third-party image/PDF libraries inside controllers.
- All routes live under `/api/v1`.
- Client-side-only tools stay fully self-contained in their page script.
