# Synthetic Sample Data Policy

Public CareFlow fixtures must be unmistakably synthetic and must not be derived from a real service-user record.

## Required conventions

- Names use labels such as `示例長者甲`, `示例家屬乙`, and `示例職員`.
- Phone numbers use `0000 0000` or `00000000`.
- Identity numbers use the visibly invalid placeholder `X000000(0)`.
- Email addresses use the reserved `.invalid` domain.
- Addresses and organizations use `示例` labels.
- Text fixtures begin with a statement that they are synthetic.
- Office files have creator and last-modified metadata removed.
- Generated image fixtures are not committed; they are recreated from source.

Do not use “fictional-looking” realistic names or valid-format contact details. They can belong to real people.

## Generate volunteer forms

From the backend environment:

```bash
python -m app.seed --only-photos
```

The generator writes ignored files under the configured asset directory. Review generator source whenever fields are added so new sample values remain obviously invalid.
