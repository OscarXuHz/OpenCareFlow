# Data Handling and Privacy Boundaries

CareFlow is a single-node demo that stores workflow state in SQLite and files on the local host. This document describes the current code, not a compliance certification.

## Data inventory

| Data | Default location | External processing | Current deletion boundary |
|---|---|---|---|
| Volunteer-form images | `backend/data/uploads/` | Azure vision when configured | No automatic lifecycle |
| Visit/meeting audio | `backend/data/visit_sessions/` | DashScope temporary OSS/ASR when configured | Transcript burn does not delete audio |
| Encrypted transcript | `backend/data/transcripts/` | Text provider receives transcript when configured | Burn overwrites/unlinks this file only |
| Transcript encryption key | `backend/data/.transcript_key` | None | Separate key rotation/recovery process required |
| PDF templates/uploads | `backend/data/templates/`, `theta_pdfs/` | Rendered pages may be sent to Azure vision | No automatic lifecycle |
| Generated XLSX/DOCX/PDF | `backend/data/exports/`, `welfare_outputs/` | Usually local after generation | No automatic lifecycle |
| Workflow records | `backend/data/careflow.db` | Selected fields may be sent to configured providers | No per-record retention policy |
| Demo Basic Auth hash | `frontend/.htpasswd.local` | Nginx only | Manual rotation/removal |

## External provider flows

- Text: the configured DeepSeek-compatible endpoint receives transcript or structured text required by the selected workflow.
- Vision: the configured Azure endpoint receives uploaded images or rendered PDF pages.
- Speech: DashScope receives audio through its temporary OSS upload/transcription flow.
- Fonts: the default frontend stylesheet requests fonts from Google Fonts.

The FastAPI service does not implement application authentication. When it is run directly, every API route is available to any client that can reach the backend port. Keep local development bound to loopback; any shared deployment must place an authenticated, access-controlled proxy in front of it.

Provider contracts, regions, logging, training use, retention, subprocessors, and deletion must be reviewed by the deploying organization. Mock mode avoids AI-provider calls but is not a security control for other network requests.

Raw vision-provider responses are not stored by default because they duplicate personal and health data in SQLite. `STORE_AI_RAW_RESPONSES=true` is a short-lived debugging option only; enabling it requires a separate retention and deletion plan.

## Review and deletion limits

The α, β, and θ workflows have backend review/state boundaries. The γ workflow currently relies on the frontend review step; its fill endpoint does not enforce a persisted approval state.

The transcript burn operation is intentionally narrow. It does not delete source audio, database metadata, rendered documents, filesystem snapshots, backups, reverse-proxy logs, provider-side data, or copied downloads.

## Operator checklist

Before handling real data:

1. add application-level authentication, authorization, and auditable user identity;
2. document purpose, lawful basis/consent, data minimization, retention, and deletion;
3. complete provider and cross-border processing review;
4. separate secrets, encryption keys, databases, and backups with least privilege;
5. configure encrypted storage, backup protection, monitoring, and incident response;
6. test deletion across local files, databases, backups, providers, and exports;
7. disable external fonts or self-host them when required;
8. run a threat model and independent security review.

## Repository rule

Git must contain only source code and explicitly synthetic fixtures. Never commit populated `.env` files, databases, logs, uploads, recordings, transcripts, identity documents, generated forms, encryption keys, or screenshots of private systems.
