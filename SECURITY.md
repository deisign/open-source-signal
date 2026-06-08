# Security Policy

Open Source Signal is a public-interest OSINT publishing toolkit. Security reports should not be filed as public GitHub issues if they contain sensitive data.

## What to report

Please report:

- exposed or hard-coded tokens, secrets or credentials;
- vulnerabilities in publishing workflows or GitHub Actions;
- unsafe handling of Telegram bot tokens, chat IDs or send logs;
- accidental publication of private personal data;
- HTML/template issues that could affect published pages;
- source-handling bugs that could expose sensitive material.

## What not to send

Do not send stolen credentials, private addresses, phone numbers, family data, full personal documents, operational targeting information, or other unnecessary sensitive data.

If an example is needed, redact it first.

## How to report

Email:

```text
editor@osintsignal.org
```

Use a short subject line:

```text
Security report: Open Source Signal
```

Include:

- affected file, workflow or page;
- what can go wrong;
- steps to reproduce, if safe;
- a minimal redacted example;
- suggested fix, if available.

## Handling

Reports are reviewed manually. Valid issues will be fixed in the repository or in site content/workflows.

Sensitive data will not be quoted in public GitHub issues, commit messages or release notes.
