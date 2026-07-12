# CareFlow 護流

[![CI](https://github.com/OscarXuHz/OpenCareFlow/actions/workflows/ci.yml/badge.svg)](https://github.com/OscarXuHz/OpenCareFlow/actions/workflows/ci.yml)
[![License: AGPL-3.0-or-later](https://img.shields.io/badge/License-AGPL--3.0--or--later-blue.svg)](LICENSE)

> AI-assisted document workflows for frontline elderly-care teams.
> 「你護老，我護你。」

CareFlow is a public, research-and-demonstration prototype for elderly-care teams. It combines a React frontend, FastAPI backend, SQLite, local file storage, and optional external AI providers. Its operating principle is simple: **AI prepares a draft; a human reviews it before operational use.**

> [!WARNING]
> CareFlow is **not** a clinical system, compliance-certified records system, or production-ready multi-tenant service. The demo's HTTP endpoint and Basic Auth do not provide application authentication, authorization, audit logging, or tenant isolation. Do not process real personal or health data until the deploying organization has completed its own security, privacy, provider, retention, and legal review.

## Status

**v0.5.0 — public source release.** The repository contains only source code and explicitly synthetic fixtures. It deliberately excludes third-party welfare-form PDFs, private credentials, runtime data, recordings, and generated outputs.

- The project is licensed under the GNU Affero General Public License, version 3 or later; see [LICENSE](LICENSE).
- CareFlow uses PyMuPDF, which is distributed under AGPL or commercial terms. The AGPL license for this project is the compatible open-source distribution path. See [Third-party notices](THIRD_PARTY_NOTICES.md).
- Welfare-form PDFs are not included. Operators must obtain permitted copies directly from their publishers as described in [backend/data/templates/README.md](backend/data/templates/README.md).

## Workflows

| Pipeline | Input | Draft output | Current review boundary |
|---|---|---|---|
| **α** Volunteer forms | Images of paper forms | Structured fields and Excel export | Backend batch/record review state before export |
| **β** Visit or meeting notes | Audio and a DOC/DOCX template | Transcript, structured slots, DOCX | Two-phase extraction then human review/render |
| **γ** Welfare forms | Elder profile and a PDF template | Field mapping and filled PDF | Review is currently enforced by the UI, not by a backend state gate |
| **θ** Custom templates | Blank PDF | Detected fields and reusable mapping | Field/bounding-box audit before publishing |

Mock mode is available when provider keys are absent. Mock output demonstrates the workflow only; it is not evidence of real extraction quality.

## Architecture

```text
Browser
  |
  v
Nginx (static React app, Basic Auth, /api reverse proxy)
  |
  v
FastAPI
  |-- SQLModel + SQLite
  |-- local uploads, templates, transcripts, and exports
  |-- in-process background tasks
  |
  +-- DeepSeek-compatible text API (optional)
  +-- Azure OpenAI / AI Foundry vision API (optional)
  +-- DashScope ASR and temporary OSS upload (optional)
```

The active implementation does not use Celery or Alembic. It is designed as a single-node demo; background work is not durable across process restarts.

For a code-level walkthrough, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Quick start with Docker

Requirements: Docker Compose v2 and OpenSSL.

```bash
git clone https://github.com/OscarXuHz/OpenCareFlow.git
cd OpenCareFlow

# Compose reads the root .env file.
cp .env.example .env

# Required by the Nginx Basic Auth configuration.
read -s CAREFLOW_DEMO_PASSWORD
printf 'careflow-demo:%s\n' "$(openssl passwd -apr1 "$CAREFLOW_DEMO_PASSWORD")" \
  > frontend/.htpasswd.local
unset CAREFLOW_DEMO_PASSWORD

# Missing provider keys use deterministic mock fallbacks.
docker compose up --build -d

curl -i http://127.0.0.1:8080/healthz
```

Open http://127.0.0.1:8080 in a browser and sign in as `careflow-demo` with the password entered above. Stop the stack with `docker compose down`.

To generate clearly synthetic volunteer-form images for a demo:

```bash
docker compose exec backend python -m app.seed --only-photos
```

The generated images and all runtime data are ignored by Git.

## Local development

### Backend

Requirements: Python 3.11 or later.

```bash
cd backend
cp .env.example .env
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
uvicorn app.main:app --reload --port 8000
```

The backend creates its SQLite tables at startup.

### Frontend

Requirements: Node.js 20 or later and npm.

```bash
cd frontend
npm ci
npm run build
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to the backend on port 8000.

## Configuration

CareFlow has three independent provider channels. Leave a channel's credentials empty to use its mock fallback.

| Channel | Main variables | Data sent when enabled |
|---|---|---|
| Text | `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_TEXT_MODEL` | Transcript or structured text needed for the selected workflow |
| Vision | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, deployment/model variables | Uploaded images or rendered PDF pages |
| Speech | `DASHSCOPE_API_KEY`, `BAILIAN_ASR_MODEL` | Audio uploaded through DashScope's temporary OSS flow |

Use the root [`.env.example`](.env.example) with Docker Compose and [`backend/.env.example`](backend/.env.example) for direct backend development. Never commit populated environment files.

## Data handling

Runtime data is stored under `backend/data/` by default. This includes uploaded source files, SQLite records, generated documents, encrypted transcripts, and the local transcript key.

Important boundaries:

- provider-enabled workflows send the minimum workflow input to the configured external provider, subject to that provider's own retention and processing terms;
- the transcript burn action removes the encrypted transcript file, but does not remove the original audio, generated output, backups, logs held elsewhere, or provider-side copies;
- Nginx Basic Auth is a demo guard, not user-level identity, RBAC, or audit logging;
- sample files must be explicitly synthetic and must not use real names, phone numbers, identity numbers, addresses, organizations, or service records.

See [docs/DATA_HANDLING.md](docs/DATA_HANDLING.md) for the full inventory and operator checklist.

## Repository layout

```text
backend/
  app/
    api/                 FastAPI routes
    llm/                 provider clients
    services/            workflow and document-processing logic
    main.py              application entry point
    config.py            environment settings
    db.py                SQLite setup and lightweight migrations
  data/                  synthetic fixtures, templates, and ignored runtime data
  tests/                 backend tests
frontend/
  src/                   React application
  nginx.conf             demo reverse proxy and security headers
docs/
  ARCHITECTURE.md
  BRAND_AESTHETIC.md
docker-compose.yml       local build/demo stack
docker-compose.deploy.yml  pre-built-image deployment example
```

## Tests and checks

```bash
cd backend
pytest
ruff check app tests

cd ../frontend
npm ci
npm run build
npm audit

cd ..
bash scripts/oss-preflight.sh
```

`oss-preflight.sh` checks the current public working tree for prohibited runtime paths, obvious credentials, and Hong Kong phone/HKID patterns. It requires Git, Bash, and Python 3. It complements—not replaces—review of all Git history, dependency licenses, and binary assets before a release.

## Deployment boundary

[`docker-compose.deploy.yml`](docker-compose.deploy.yml) is an example for images your organization has built and published. Set `CAREFLOW_BACKEND_IMAGE` and `CAREFLOW_FRONTEND_IMAGE` in the root `.env`. The file does not point to official CareFlow images and is not a production security architecture.

Before any shared deployment, use HTTPS, add application-level authentication and authorization, isolate encryption keys and backups, set retention and deletion policies, complete provider/privacy review, and obtain an independent security review. Basic Auth alone is not enough.

## Contributing and security

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Report vulnerabilities or accidental personal-data exposure through the private process in [SECURITY.md](SECURITY.md), never through a public issue.

## License

CareFlow is licensed under the GNU Affero General Public License, version 3 or later. The license covers CareFlow source code only; it does not grant rights to third-party provider services, fonts, dependencies, or welfare-form PDFs. Review [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before redistributing a modified version or deploying it for users over a network.
