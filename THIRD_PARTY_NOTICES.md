# Third-Party Notices and Release Blockers

This file records known licensing boundaries for open-source preparation. It is not a complete software bill of materials or legal advice.

## PyMuPDF / MuPDF

CareFlow directly uses PyMuPDF for PDF rendering, extraction, form filling, and template analysis. PyMuPDF and MuPDF are offered under the GNU AGPL and commercial licenses. The project must choose and document a compliant route before public distribution of the repository or container images:

- comply with the applicable AGPL requirements;
- obtain an appropriate commercial license; or
- replace PyMuPDF with a dependency compatible with the selected CareFlow distribution model.

Official licensing information: <https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright>

## Bundled PDF forms

The following source forms are third-party works and are not covered by CareFlow's source-code license:

- `backend/data/templates/CCSV_application_form_(September_2023)_CHI_W3C_proceeded.pdf`
- `backend/data/templates/CSSA_Registration_Form_c_2025-10.pdf`
- `backend/data/templates/OALA_Simplified Form and notice_chi_012025 rev.pdf`
- `backend/data/templates/Online_SWD307_SSA_Application_Form_(Rev)(9_2023).pdf`
- `backend/data/templates/joyyou_apply.pdf`

Redistribution permission has not been documented in this repository, so these files are excluded from the public working tree. Operators must obtain permitted copies from the official publishers. If the project later bundles a form, it must first obtain written permission and document the exact terms.

## Frontend fonts

The frontend requests Noto Serif TC and JetBrains Mono from Google Fonts at runtime. Those requests disclose the user's IP address and browser metadata to a third party. A privacy-sensitive deployment should self-host appropriately licensed font files or use a system-font stack.

## Transitive packages

Frontend and backend dependencies retain their own licenses. The release process must generate and review a dependency license report and software bill of materials. In particular, preserve attribution required by data packages such as `caniuse-lite`.
