# JSX Quick Start Guide

## Installation

```bash
# Clone repository
git clone https://github.com/xerog-exe/JSX.git
cd JSX

# Install dependencies
pip install -r requirements.txt
```

## Quick Commands

### Scan Local File
```bash
python JSX.py --file path/to/script.js
```

### Scan Remote URL
```bash
python JSX.py --url https://example.com/app.js
```

### Export to JSON
```bash
python JSX.py --file script.js --json results.json
```

### Get Help
```bash
python JSX.py --help
```

## Understanding Output

**Color Coding:**
- 🔴 **RED (HIGH)** - Critical secrets: AWS keys, API keys, tokens, passwords
- 🟡 **YELLOW (MEDIUM)** - Sensitive data: Internal URLs, email lists
- 🔵 **BLUE (LOW)** - General info: External URLs, IP addresses

**Each Finding Shows:**
- **Value**: The detected secret/data
- **Context**: Surrounding code (helps verify it's real)
- **Severity**: HIGH, MEDIUM, or LOW

## Example Usage

### Find all secrets in a React bundle
```bash
python JSX.py --file build/bundle.js --json report.json
```

### Scan a CDN-hosted file
```bash
python JSX.py --url https://cdn.example.com/main.js
```

### CI/CD Integration
```bash
python JSX.py --file app.js --json audit.json
python parse_results.py audit.json  # Your custom result parser
```

## Adding a Custom Detector

1. Create `jsx/detectors/mydetector.py`:

```python
import re
from .base import BaseDetector

class Detector(BaseDetector):
	def __init__(self):
		super().__init__("My Detector", severity="high")
		self.pattern = re.compile(r'PATTERN_HERE')

	def run(self, content):
		findings = []
		for match in self.pattern.finditer(content):
			findings.append({
				"value": match.group(0),
				"context": self._get_context(content, match.start()),
				"severity": "high"
			})
		return findings
```

2. Run JSX - it auto-loads the detector!

## What JSX Detects

| Type | Severity | Example |
|------|----------|---------|
| AWS Keys | HIGH | AKIAIOSFODNN7EXAMPLE |
| JWT Tokens | HIGH | eyJhbGci... |
| API Keys | HIGH | AIza... |
| Passwords | HIGH | password: "secret123" |
| Bearer Tokens | HIGH | Bearer eyJ... |
| Firebase | HIGH | firebaseConfig = {...} |
| Emails | LOW | admin@example.com |
| URLs | LOW | https://internal.company.com |
| IPs | LOW | 192.168.1.100 |

## JSON Output Format

```json
{
  "grouped": {
	"Email Addresses": [...],
	"AWS Access Keys": [...]
  },
  "all": [all findings flattened]
}
```

## Tips & Tricks

✅ **Best Practices:**
- Always verify findings manually
- Check context to avoid false positives
- Secure JSON exports (they contain secrets!)
- Use in CI/CD to catch leaks early

⚠️ **Limitations:**
- Won't find encoded/obfuscated secrets
- Can't detect custom secret formats
- False positives possible (review context)

## Troubleshooting

**Error: ModuleNotFoundError**
```bash
pip install requests
```

**No findings detected?**
- Check file path
- Verify JavaScript is not minified
- Try with sample_test.js first

**Slow scanning?**
- Large files take longer
- Try smaller sections first
- Consider splitting files

## Support

- **GitHub Issues**: https://github.com/xerog-exe/JSX/issues
- **Main README**: See README.md for detailed documentation

---

**Remember**: Use JSX responsibly during authorized security testing only! 🛡️
