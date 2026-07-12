# Source PDF templates

Third-party welfare and application forms are intentionally not distributed with the public CareFlow source tree.

The JSON mappings in `../form_templates/` are version-specific. To use one:

1. obtain the exact form version from its official publisher;
2. confirm that your use and local storage comply with the publisher's terms;
3. place the PDF in this directory using the `source_pdf` filename declared by the mapping;
4. verify the form version and field coordinates before processing any record.

A missing source PDF is reported as `source_required` by the template-list API. Do not commit downloaded forms unless the project has documented redistribution permission.
