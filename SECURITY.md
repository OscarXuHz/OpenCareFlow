# Security Policy

## Project status

CareFlow is a research/demo prototype. No released version is currently approved for production handling of personal or health data. Basic Auth protects the whole demo but does not provide per-user identity, roles, tenant isolation, or a complete audit trail.

## Private reporting

Do not open a public issue for:

- a vulnerability;
- an exposed credential;
- personal, health, identity, or organization-confidential data;
- a repository history object that should have been removed.

Use the repository's **Security** tab and select **Report a vulnerability** to open a private security advisory. If private reporting is unavailable, contact the repository owner privately through GitHub before sharing details. Include affected versions, reproduction steps, impact, and a safe way to validate the fix. Do not attach real service-user data.

## Accidental data exposure

Treat committed secrets or personal data as an incident:

1. stop publication and disable affected deployments;
2. revoke or rotate the credential immediately;
3. preserve the minimum evidence needed for investigation outside the public repository;
4. remove the data from every reachable Git ref, fork, artifact, cache, image, and release;
5. verify provider-side and backup retention separately;
6. require collaborators to re-clone after a history rewrite.

Deleting a file in a later commit is not sufficient.

## Deployment boundary

Organizations deploying CareFlow are responsible for authentication, access control, backups, encryption keys, provider agreements, retention, monitoring, incident response, and applicable privacy/legal review. See [docs/DATA_HANDLING.md](./docs/DATA_HANDLING.md).
