# CareFlow 護流

> AI-assisted document workflows for frontline elderly-care teams.
> 「你護老，我護你。」

CareFlow is a research and demonstration prototype built around one rule: AI prepares a draft and a human reviews it before operational use. It combines a React frontend, a FastAPI backend, SQLite, local file storage, and optional external AI providers.

> [!WARNING]
> CareFlow is not a clinical system, compliance-certified records system, or production-ready multi-tenant service. Do not process real personal or health data until your organization has completed its own security, privacy, provider-contract, retention, and legal review.

## Release status

This repository is being prepared for public release. Do not make it public yet. The remaining release blockers are:

- remove sensitive data and credentials from every Git ref, or publish a clean snapshot;
- rotate all credentials that ever appeared in Git history;
- resolve the PyMuPDF AGPL/commercial licensing path;
- obtain contributor approval for the selected project license;
- remove or obtain redistribution permission for bundled third-party PDF forms.

See [Third-party notices](./THIRD_PARTY_NOTICES.md) for the current licensing boundary.

## Workflows

| Pipeline | Input | Draft output | Current review boundary |
|---|---|---|---|
| **α** Volunteer forms | Images of paper forms | Structured fields and Excel export | Backend batch/record review state before export |
| **β** Visit or meeting notes | Audio and a DOC/DOCX template | Transcript, structured slots, DOCX | Two-phase extraction then human review/render |
| **γ** Welfare forms | Elder profile and a PDF template | Field mapping and filled PDF | Review is currently enforced by the UI, not by a backend state gate |
| **θ** Custom templates | Blank PDF | Detected fields and reusable mapping | Field/bounding-box audit before publishing |

Mock mode is available when provider keys are absent. Mock output demonstrates the workflow only; it is not evidence of real extraction quality.

Third-party welfare-form PDFs are not included in the public tree. Operators must obtain permitted copies from the publishers and place them as described in [backend/data/templates/README.md](./backend/data/templates/README.md).

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

For a code-level walkthrough, see [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).

## Quick start with Docker

Requirements: Docker Compose and OpenSSL.

```bash
git clone https://github.com/OscarXuHz/CareFlow.git
cd CareFlow

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
open http://127.0.0.1:8080
```

Stop the stack with `docker compose down`.

To generate clearly synthetic volunteer-form images for a demo:

```bash
docker compose exec backend python -m app.seed --only-photos
```

The generated images and all runtime data are ignored by Git.

## Local development

### Backend

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

Use the root [`.env.example`](./.env.example) with Docker Compose and [`backend/.env.example`](./backend/.env.example) for direct backend development. Never commit populated environment files.

## Data handling

Runtime data is stored under `backend/data/` by default. This includes uploaded source files, SQLite records, generated documents, encrypted transcripts, and the local transcript key.

Important boundaries:

- provider-enabled workflows send the minimum workflow input to the configured external provider, subject to that provider's own retention and processing terms;
- the transcript burn action removes the encrypted transcript file, but does not remove the original audio, generated output, backups, logs held elsewhere, or provider-side copies;
- Nginx Basic Auth is a demo guard, not user-level identity, RBAC, or audit logging;
- sample files must be explicitly synthetic and must not use real names, phone numbers, identity numbers, addresses, organizations, or service records.

See [docs/DATA_HANDLING.md](./docs/DATA_HANDLING.md) for the full inventory and operator checklist.

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
```

The release gate also requires a clean-clone test with no private `.env`, a secret scan across all refs, and a review of bundled binary assets.

## Deployment boundary

[`docker-compose.deploy.yml`](./docker-compose.deploy.yml) is an example for images your organization has built and published. Set `CAREFLOW_BACKEND_IMAGE` and `CAREFLOW_FRONTEND_IMAGE` in the root `.env`. The file does not point to official CareFlow images, and it should not be treated as a production security architecture.

## Contributing and security

Read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a pull request. Report vulnerabilities or accidental personal-data exposure through the private process in [SECURITY.md](./SECURITY.md), never through a public issue.

## License

A project license decision is still pending public-release clearance. The source tree currently contains an MIT [LICENSE](./LICENSE), but PyMuPDF is offered under AGPL or a commercial license, and bundled third-party forms are not covered by the CareFlow source license. Resolve those items before distributing the repository or container images.
