# JSX - JavaScript Secret Scanner (v0.2)

**JSX (JavaScript Secret by Xerog)** is a command-line tool to scan JavaScript files for potentially sensitive information and secrets. Version v0.2 improves usability and output quality: masked secrets by default, occurrence counts, line numbers, confidence scores, summary output, and richer CLI flags to control output.

## 🎯 Purpose

During security testing and bug bounty engagements, JavaScript files often contain exposed secrets, API keys, authentication tokens, and other sensitive information. Manually inspecting every JavaScript file is time-consuming and error-prone. JSX automates this process by:

- Scanning JavaScript files (local or remote) for known secret patterns
- Categorizing findings by type and severity
- Providing context around each discovery
- Exporting results in JSON format for further analysis
- Supporting modular detector extensions

## 🚀 Features

- **Multiple Input Sources**: Scan local JavaScript files or remote URLs
- **9 Built-in Detectors**:
  - Email Addresses
  - URLs (internal and external)
  - IP Addresses
  - JWT Tokens
  - Google API Keys
  - Firebase Configuration
  - AWS Access Keys
  - Authorization Tokens (Bearer tokens)
  - Hardcoded Credentials (passwords, secrets, tokens)

- **Severity Classification**: HIGH, MEDIUM, LOW severity levels
- **Colored Terminal Output**: Easy-to-read, color-coded results
- **Context Display**: Shows surrounding code for each finding
- **JSON Export**: Export results for reporting and further processing
- **Modular Architecture**: Easy to add custom detectors
- **No false positives**: Conservative regex patterns

## 📋 Requirements

- Python 3.7 or higher
- `requests` library for remote URL fetching

## 💾 Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/xerog-exe/JSX.git
cd JSX
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually install requests:

```bash
pip install requests
```

## 🔧 Usage

### Basic Syntax

```bash
python JSX.py [OPTIONS]
```

### Command-Line Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--file` | `-f` | Path to local JavaScript file to scan | `python JSX.py --file app.js` |
| `--url` | `-u` | Remote JavaScript file URL to scan | `python JSX.py --url https://example.com/app.js` |
| `--json` | `-j` | Export results to JSON file (dest: json_output) | `python JSX.py --file app.js --json results.json` |
| `--help` | `-h` | Show help message | `python JSX.py --help` |
| `--context` | | Show surrounding code context for each finding | `python JSX.py --file app.js --context` |
| `--show-full` | | Show full secret values (do not mask) | `python JSX.py --file app.js --show-full` |
| `--summary-only` | | Show only a compact summary of the scan | `python JSX.py --file app.js --summary-only` |
| `--severity` | | Filter findings by severity (low, medium, high, info) | `python JSX.py --file app.js --severity high` |
| `--detector` | | Filter findings by detector name (exact match) | `python JSX.py --file app.js --detector "JWT Tokens"` |
| `--report-md` | | Export a Markdown report to the given file path | `python JSX.py --file app.js --report-md report.md` |
| `--report-html` | | Export an HTML report to the given file path | `python JSX.py --file app.js --report-html report.html` |

## 📖 Usage Examples

### Scan a Local JavaScript File

```bash
python JSX.py --file ./app.js
```

**Output:**
```
Loading content...
Content loaded
Scanning content...
Scan complete

Authorization Tokens
  HIGH Bearer eyJhbGciOiJIUzI1Ni...  (1x)
    Line(s): 12
    Confidence: 95%

Email Addresses
  LOW admin@example.com  (2x)
    Line(s): 5, 45

AWS Access Keys
  HIGH AKIA************EXAM  (1x)
    Line(s): 20
    Confidence: 90%
```

### Scan a Remote JavaScript File

```bash
python JSX.py --url https://example.com/static/app.js
```

JSX will fetch the JavaScript from the remote URL and scan it.

### Scan with JSON Export

```bash
python JSX.py --file ./script.js --json results.json
```

This creates a `results.json` file with all findings in structured JSON format. Each finding entry includes:

- value (masked unless `--show-full` used)
- detector
- severity
- occurrences
- lines
- confidence

Example snippet:

```json
{
  "grouped": {
    "Authorization Tokens": [
      {
        "value": "Bearer eyJhbGciOiJIUzI1Ni...",
        "detector": "Authorization Tokens",
        "severity": "high",
        "occurrences": 1,
        "lines": [12],
        "confidence": 95
      }
    ]
  },
  "all": [ /* flattened list */ ]
}
```

### Combine Options

```bash
python JSX.py --url https://cdn.example.com/bundle.js --json report.json
```

This fetches a remote file, scans it, and exports results to JSON.

## 🔍 Detectors

### Email Addresses
- **Severity**: LOW
- **Pattern**: Standard email format
- **Use Case**: Identifying potential user accounts or contact information

### URLs
- **Severity**: LOW
- **Pattern**: HTTP/HTTPS URLs
- **Use Case**: Finding internal endpoints or services

### IP Addresses
- **Severity**: LOW
- **Pattern**: IPv4 addresses
- **Use Case**: Identifying internal network infrastructure

### JWT Tokens
- **Severity**: HIGH
- **Pattern**: JWT format (eyJ...)
- **Use Case**: Finding authentication tokens that could be exploited

### Google API Keys
- **Severity**: HIGH
- **Pattern**: AIza[0-9A-Za-z\-_]{35}
- **Use Case**: Finding exposed Google Cloud credentials

### Firebase Configuration
- **Severity**: HIGH
- **Pattern**: Firebase config objects and API keys
- **Use Case**: Identifying Firebase backend configuration

### AWS Access Keys
- **Severity**: HIGH
- **Pattern**: AKIA[0-9A-Z]{16}
- **Use Case**: Finding AWS credentials that could grant cloud access

### Authorization Tokens
- **Severity**: HIGH
- **Pattern**: Bearer tokens and authorization headers
- **Use Case**: Finding authentication credentials

### Hardcoded Credentials
- **Severity**: HIGH
- **Pattern**: password=, secret=, client_secret= assignments
- **Use Case**: Finding hardcoded credentials in source code

## 🛠️ Adding Custom Detectors

The modular architecture makes it easy to add new detectors. Here's how:

### Create a New Detector

1. Create a new file in `jsx/detectors/` (e.g., `jsx/detectors/custom_detector.py`):

```python
"""Custom detector for API tokens."""

import re
from .base import BaseDetector


class Detector(BaseDetector):
    """Detects custom API tokens."""

    def __init__(self):
        super().__init__("Custom API Tokens", severity="high")
        self.pattern = re.compile(r'CUSTOM_[A-Z0-9]{32}')

    def run(self, content):
        """Find all custom API tokens."""
        findings = []
        seen = set()

        for match in self.pattern.finditer(content):
            value = match.group(0)
            if value in seen:
                continue
            seen.add(value)

            context = self._get_context(content, match.start())
            findings.append({
                "value": value,
                "context": context,
                "severity": "high"
            })

        return findings
```

2. The detector will be automatically loaded and used on the next scan!

## 📁 Project Structure

```
JSX/
├── JSX.py                      # Main entry point
├── jsx/
│   ├── __init__.py
│   ├── cli.py                  # Command-line interface
│   ├── scanner.py              # Core scanning engine
│   └── detectors/
│       ├── __init__.py
│       ├── base.py             # Base detector class
│       ├── emails.py
│       ├── urls.py
│       ├── ips.py
│       ├── jwt.py
│       ├── googleApiKey.py
│       ├── firebase.py
│       ├── awsKeys.py
│       ├── authTokens.py
│       └── credentials.py
├── requirements.txt
├── README.md
├── LICENSE.txt
└── sample_test.js             # Example test file
```

## 🎓 Real-World Examples

### Example 1: Scan a React Application

```bash
python JSX.py --file ./src/App.js --json findings.json
```

### Example: Summary-only output

```bash
python JSX.py --file ./bundle.js --summary-only
```

```
Scan Summary

Emails              5
URLs                8
IP Addresses        6
JWT Tokens          3
Google API Keys     3
AWS Keys            1
Firebase            2

High Severity       9
Medium Severity     2
Low Severity        19

Scan Time           0.42 sec
```
Generated reports
---------------

During local testing the CLI also generates report files you can review in the repository root:

- report.md — a Markdown export of the last scan (human readable)
- report.html — a simple HTML export you can open in a browser

To reproduce the test and create these reports locally run:

```bash
python JSX.py --file sample_test.js --report-md report.md --report-html report.html
```

After running the command above you can open `report.md` in any editor or `report.html` in a browser to review the findings and screenshots. If you'd like, I can add small example PNGs into `docs/screenshots/` and commit them to the repo — tell me and I'll add two simple placeholders (1x1 PNGs) or real captures from your environment.


### Example 2: Scan a CDN-hosted Bundle

```bash
python JSX.py --url https://cdn.myapp.com/main.bundle.js
```

### Example 3: Security Audit Pipeline

```bash
# In a CI/CD pipeline
python JSX.py --file ./build/app.js --json audit_results.json

# Check for HIGH severity findings
python -c "
import json
with open('audit_results.json') as f:
    results = json.load(f)
    high_findings = [f for f in results['all'] if f['severity'] == 'high']
    if high_findings:
        print(f'Found {len(high_findings)} high-severity findings!')
        exit(1)
"
```

## 📊 Output Interpretation

### Severity Levels

- **HIGH** 🔴: Critical secrets that could grant system access or compromise security
  - AWS keys, API keys, JWT tokens, passwords
  - **Action Required**: Immediately rotate or invalidate

- **MEDIUM** 🟡: Potentially sensitive information that could be misused
  - Internal URLs, email addresses (if enumerated)
  - **Action Required**: Review context and assess risk

- **LOW** 🟢: General information that aids reconnaissance but isn't immediately dangerous
  - External URLs, IP addresses, email addresses
  - **Action Required**: Monitor for exposure patterns

### Context Display

Each finding shows surrounding code to help understand:
- Where the secret is used
- How it's assigned or referenced
- Whether it's hardcoded or from configuration

## ⚠️ Limitations & Notes

- **False Positives**: Some patterns may match non-secret strings. Always verify findings.
- **Obfuscated Code**: Minified or obfuscated JavaScript may be harder to parse.
- **Encoded Secrets**: Base64 or otherwise encoded secrets won't be detected.
- **Remote Fetching**: Requires internet access and the target server to allow downloads.
- **Large Files**: Very large JavaScript files may take time to scan.

## 🔒 Security Considerations

- **JSX Output**: Results contain actual secrets. Secure the output files.
- **Network Traffic**: Remote URL fetches are sent over HTTPS by default.
- **Local Scanning**: Only scans provided files; doesn't scan your system.

## 🚀 Roadmap (Future Features)

- [ ] Website crawling to automatically discover JavaScript files
- [ ] Concurrent scanning for multiple files
- [ ] HTML report generation
- [ ] Database of findings for trend analysis
- [ ] API endpoint validation
- [ ] Endpoint discovery from JavaScript
- [ ] Configuration file support
- [ ] Integration with security platforms

## 🤝 Contributing

Contributions are welcome! Ways to contribute:

1. **Add New Detectors**: Create detectors for other secret patterns
2. **Improve Patterns**: Enhance existing regex patterns
3. **Bug Reports**: Report issues or false positives
4. **Feature Requests**: Suggest new functionality

## 📄 License

This project is licensed under the MIT License - see the LICENSE.txt file for details.

## 👨‍💻 Author

**Xerog** - Security Research & Development

## ❓ FAQ

**Q: Will JSX find all secrets?**
A: No tool finds 100% of secrets. JSX uses pattern matching for known secret formats. It won't find custom, encoded, or obfuscated secrets.

**Q: Can I use JSX on production code?**
A: Yes, JSX only reads files; it doesn't modify anything. Use it as part of security audits.

**Q: How fast is JSX?**
A: Speed depends on file size. Most JavaScript files scan in milliseconds.

**Q: Can I use JSX in CI/CD?**
A: Yes! Export to JSON and parse results in your pipeline.

**Q: What if a legitimate token matches the pattern?**
A: Review the context. Some matches may be test tokens or examples. Verify before alerting.

**Q: How do I add a custom detector?**
A: Create a new Python file in `jsx/detectors/` inheriting from `BaseDetector`. See "Adding Custom Detectors" section.

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub: https://github.com/xerog-exe/JSX/issues
- Check existing documentation

---

**Stay Secure! 🛡️**

JSX helps you discover exposed secrets before attackers do. Use it responsibly during authorized security testing.
