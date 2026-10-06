# Changelog

All notable changes to this project. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.0.0] - 2026-10-06

A rebuild of the 2019 site with the same look and features on a modern stack.

### Added
- FastAPI app with server-rendered Jinja2 pages: home, event pages, event registration, hackathon page and team registration.
- One YAML content file for the edition (events, rules, dates, FAQ), validated at start-up.
- Organiser console: login, dashboard with counts per event, participant search and filter, hackathon teams, delete, abstract download.
- Exports generated on request: one Excel workbook (all participants, a sheet per event, hackathon teams), per-event workbooks and CSV.
- Registration rules on the server: 2 technical and 2 non-technical events at most, unique e-mail and mobile, hackathon-only teams of 3–5.
- Abstract uploads checked by content (PDF or DOCX), size-limited and stored under random names.
- SQLAlchemy 2 models with Alembic migrations, for SQLite and PostgreSQL.
- Fictional demo data (`python -m app.seed`).
- 43 pytest tests, Ruff, Dockerfile, Docker Compose with PostgreSQL, and GitHub Actions CI.
- README, DEVELOPMENT guide, contributing notes, screenshots and an MIT license.

### Changed
- The black and neon green design, the Exo 2 typeface and the "WELCOMES YOU" scramble were rebuilt in plain CSS and JavaScript, responsive and accessible, with no jQuery.
- Exo 2 is self-hosted as WOFF2 (converted from the original OTF files) with its OFL license.
- Event write-ups were rewritten from the 2019 pages, and organiser phone numbers were replaced with one contact address.
- The hackathon page and form now use the same design as the rest of the site.
- The abstract template's document properties no longer carry a personal name.

### Removed
- The PHP pages, `config.php` and `synsara-db.sql`.
- PHPExcel, jQuery 1.11 and the other bundled vendor libraries.
- The hackathon site forked from another project's template (the "HackShetra" files) and its separate form.
- Committed `.xlsx` registration files with test data, tutorial notes, temporary files and `Thumbs.db`/`.DS_Store` files.
- The open "Sign up" page for organiser accounts.

### Security
- No secrets or personal data in the tree. Settings come from environment variables.
- CSRF tokens on every form, a signed session cookie for organisers and a strict Content Security Policy.
- Spreadsheet formula-injection guard on exports.
- **The 1.0.0 commit is still in the history** and contains a MySQL username and password in `config.php`, plus test registrations with personal phone numbers and e-mails in `downloads/*.xlsx`. Treat that password as compromised.

## [1.0.0] - 2019-09

The original SYNSARA 2K19 website (committed to GitHub on 2020-09-26).

- PHP and MySQL site with event registration, hackathon registration with abstract upload and organiser login.
- Registrations appended to Excel files with PHPExcel.
- HTML5 Boilerplate base, jQuery, Exo 2 font.

[2.0.0]: https://github.com/imkarthiknr/synsara-2019/compare/408f3a2...master
[1.0.0]: https://github.com/imkarthiknr/synsara-2019/tree/408f3a2
