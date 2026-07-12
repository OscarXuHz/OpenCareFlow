# Contributing to CareFlow

CareFlow welcomes contributions that improve its safety, accessibility, reliability, and documentation. By submitting a pull request, you confirm that you have the right to submit the work and agree to license your contribution under the GNU Affero General Public License, version 3 or later.

## Before opening a change

- Do not include real personal data, health information, recordings, identity documents, API responses, credentials, logs, databases, or organization-confidential material.
- Use only clearly synthetic fixtures. Follow [docs/SAMPLE_DATA.md](./docs/SAMPLE_DATA.md).
- Report vulnerabilities or accidental data exposure privately as described in [SECURITY.md](./SECURITY.md).
- Keep AI output behind the existing human-review boundary. If a workflow has only a UI review gate, call that limitation out explicitly.

## Development setup

Backend:

```bash
cd backend
cp .env.example .env
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ruff check app tests
```

Frontend:

```bash
cd frontend
npm ci
npm run build
npm audit --omit=dev
```

Docker:

```bash
cp .env.example .env
read -s CAREFLOW_DEMO_PASSWORD
printf 'careflow-demo:%s\n' "$(openssl passwd -apr1 "$CAREFLOW_DEMO_PASSWORD")" \
  > frontend/.htpasswd.local
unset CAREFLOW_DEMO_PASSWORD
docker compose up --build -d
```

## Pull requests

A pull request should:

- explain the user-facing behavior and privacy impact;
- include tests for changed backend behavior;
- pass backend tests, Ruff, frontend build, and the public-repository preflight;
- avoid unrelated generated files or formatting churn;
- update architecture, configuration, or data-handling docs when a boundary changes;
- identify any new dependency and its license.

By contributing, you confirm that you have the right to submit the work and agree to license it under the GNU Affero General Public License, version 3 or later.
