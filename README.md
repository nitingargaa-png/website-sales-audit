## Cross-project dependency

This project requires `website-audit-builder` to be present as a sibling directory:

    parent/
    ├── website-sales-audit/        (this project)
    └── website-audit-builder/      (required sibling)

The `execution/extract_business_data.py` script lives canonically in `website-audit-builder/execution/`. This project invokes it via subprocess at runtime. If you clone this project standalone without `website-audit-builder` next to it, website generation will fail with a FileNotFoundError.
