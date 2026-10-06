# Contributing

Thanks for taking a look. This is a personal portfolio project, but issues and pull requests are welcome.

## Getting started

Follow [DEVELOPMENT.md](DEVELOPMENT.md) to set up, then:

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest
```

## Pull requests

- Keep each pull request to one change, and describe what it changes and why.
- Add or update tests for behaviour changes. Rules live in `app/services/`, so most tests belong in `tests/test_rules.py`.
- If you change `app/models.py`, add a migration (`uv run alembic revision --autogenerate -m "..."`) and review it.
- Keep the Content Security Policy strict: no inline `<script>` or `style=""`. Put styles in `site.css` and behaviour in `site.js`.
- Never commit real personal data, uploads, `.env` files or database files. Use `example.com` addresses in tests and demo data.
- Update the README or DEVELOPMENT guide when you change how something is run or configured, and add a line to the CHANGELOG.

## Commit messages

Use the imperative mood with a short summary line, for example `Add CSV export for hackathon teams`.

## Reporting security issues

Please don't open a public issue for a vulnerability. Contact the maintainer through the e-mail address on their [GitHub profile](https://github.com/imkarthiknr) instead.
