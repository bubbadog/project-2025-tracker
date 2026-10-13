# Security

This repository holds a static site and JSON data; it runs no server and stores no user data. Even so, there are things worth reporting privately:

- A way to make the GitHub Actions workflows run untrusted code or reach a secret.
- A way for a pull request to publish content to the site without passing the checks.
- Personal information about anyone that has reached the data, the site, an issue or a commit (the project is published anonymously, and private people are never named).
- A dependency or pinned action with a known vulnerability that Dependabot has not flagged.

## How to report

Use GitHub's private vulnerability reporting: **Security** tab, then **Report a vulnerability**. It opens a private thread with the maintainer. Please do not open a public issue for any of the items above.

If the report is about personal information that has already been published, say which file or page, and it will be removed from the current version and from history (history rewriting is treated as cleanup; the removal from the live site comes first).

## What to expect

- Acknowledgement within 72 hours.
- A fix or a decision within 14 days for anything that affects the site or the workflows.
- Credit in the release notes if you want it, under whatever name you choose.

## Scope notes

- Errors in the data (a wrong status, a stale link) are not security issues: use the [Report an error](../../issues/new?template=report-error.yml) form.
- The workflows run with read-only tokens and pinned actions; the deploy job is the only one with write permissions, and it writes only to GitHub Pages. If you find otherwise, that is a report.
