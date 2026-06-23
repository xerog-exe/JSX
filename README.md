# JSX - JavaScript Secret Scanner

JSX (JavaScript Secret by Xerog) is a command-line tool to scan JavaScript files (local or remote) for potentially sensitive information: emails, URLs, IP addresses, tokens, API keys, and other secrets.

Usage:

- Scan a local file:
  jsx --file ./script.js

- Scan a remote file:
  jsx --url https://example.com/static/app.js

- Export JSON results:
  jsx --file ./script.js --json results.json

Design:
- Modular detectors located in lib/detectors/*.js. Add detectors by creating new modules that export a run(content) function.
- Pretty terminal output and JSON export.

Future:
- Crawl targets and discover JS files
- Concurrent scanning, endpoint validation, HTML reports, database of findings

License: MIT
