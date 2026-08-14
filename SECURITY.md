# Security Policy

## Supported Versions

Clipper is a small, local-first project and is currently under active development.

Security fixes will generally be applied to the latest version of the project. Older versions may not receive security updates.

| Version | Supported |
| ------- | --------- |
| Latest  | ✅ |
| Older releases | ❌ |

## Reporting a Vulnerability

If you discover a security vulnerability in Clipper, please **do not open a public GitHub issue** with the details.

Instead, report it privately through GitHub's **Security Advisories** feature:

**Repository → Security → Advisories → Report a vulnerability**

Please include as much of the following information as possible:

- A clear description of the vulnerability
- Steps to reproduce the issue
- The affected file, component, or endpoint
- The potential impact
- Any proof-of-concept code or screenshots, if applicable
- A suggested fix, if you have one

I'll review legitimate reports and work on a fix before publicly disclosing the issue.

## What Counts as a Security Issue?

Examples include:

- Remote code execution
- Arbitrary file access
- Path traversal
- Command injection
- Authentication or authorization bypass
- Unsafe handling of user-controlled URLs or input
- Exposure of sensitive local files or information
- Vulnerabilities that could affect the machine running Clipper

Bugs that only cause normal application errors, unsupported URLs, failed downloads, or incorrect video output generally aren't considered security vulnerabilities.

## Scope

Clipper is designed to run locally on the user's own machine. It is **not intended to be deployed as a publicly accessible internet service without additional security controls**.

Because of this, issues involving an attacker already having unrestricted access to the machine running Clipper may be outside the project's intended threat model.

Third-party dependencies such as **yt-dlp, Flask, and ffmpeg** are maintained by their respective projects. Vulnerabilities originating entirely within those projects should generally be reported to their maintainers as well.

## Responsible Disclosure

Please give reasonable time for a vulnerability to be investigated and fixed before publicly disclosing technical details.

Security reports made in good faith are appreciated. Please avoid accessing, modifying, or deleting data that does not belong to you while testing a vulnerability.

## Disclaimer

Clipper is provided **"as is"** without warranty. The project does not guarantee that the software is free from security vulnerabilities or that it will behave safely in every environment.

Users should keep Clipper and its dependencies updated and should avoid exposing the local server to untrusted networks unless they understand and have addressed the associated risks.
