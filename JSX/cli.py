"""Command-line interface for JSX scanner."""

import argparse
import json
import sys
import re
import html as html_escape
from datetime import datetime
from pathlib import Path

import requests

from .scanner import Scanner


def format_color(text, color):
    """Apply ANSI color code to text."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "dim": "\033[90m",
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }
    start = colors.get(color, "")
    reset = colors.get("reset", "")
    return f"{start}{text}{reset}"


def load_content(file_path=None, url=None):
    """Load JavaScript content from file or URL."""
    if file_path:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return path.read_text("utf-8")

    if url:
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch {url}: {e}")

    raise ValueError("Must provide either --file or --url")


def mask_value(value, show_full=False):
    """Mask sensitive values by default. Return masked string."""
    if show_full or not isinstance(value, str):
        return value

    try:
        if value.count('.') == 2 and len(value) > 20:
            return value[:24] + '...'
    except Exception:
        pass

    if isinstance(value, str) and value.startswith('AIza') and len(value) > 10:
        return value[:4] + '*' * (len(value) - 8) + value[-4:]

    if isinstance(value, str) and value.startswith('AKIA') and len(value) >= 16:
        return value[:4] + '*' * (len(value) - 8) + value[-4:]

    if isinstance(value, str) and len(value) > 12:
        return value[:6] + '*' * (len(value) - 10) + value[-4:]

    return value
def normalize_value(raw):
    """If detectors returned a large object/string as value, try to extract a token-like substring.

    This defends against detectors that mistakenly return whole JSON blobs as the value.
    """
    if not raw or not isinstance(raw, str):
        return raw

    if len(raw) < 120 and "\n" not in raw and "{" not in raw and "[" not in raw:
        return raw

    patterns = [
        re.compile(r'eyJ[0-9A-Za-z\-_]+\.[0-9A-Za-z\-_]+\.[0-9A-Za-z\-_]+'),
        re.compile(r'AIza[0-9A-Za-z\-_]{35}'),
        re.compile(r'AKIA[0-9A-Z]{16}'),
        re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3})\b'),
        re.compile(r'https?://[\w\-\.\/:?=&%#\+~,]+'),
        re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
    ]

    for p in patterns:
        m = p.search(raw)
        if m:
            return m.group(0)

    return raw.strip().replace('\n', ' ')[:120]



def print_results(results):
    """Print results in a formatted, colored manner.

    Note: printing options (context, show_full, filters) are handled in main().
    """
    grouped = results.get("grouped", {})
    categories = [k for k, v in grouped.items() if v]

    if not categories:
        print(format_color("\nNo findings detected.", "green"))
        return

    print("")
    for category in categories:
        findings = grouped[category]
        print(format_color(category, "underline"))
        for finding in findings:
            severity = finding.get("severity", "info")
            value = finding.get("value", "")
            occurrences = finding.get("occurrences", 1)
            lines = finding.get("lines", [])

            sev_color = {"high": "red", "medium": "yellow", "low": "cyan", "info": "cyan"}.get(severity, "cyan")
            sev_text = format_color(severity.upper(), sev_color)
            value_text = format_color(value, "white")

            print(f"  {sev_text} {value_text}  {format_color(f'({occurrences}x)', 'dim')}")
            if lines:
                print(f"    Line(s): {', '.join(str(l) for l in lines)}")
        print("")


def export_json(results, output_path):
    """Export results to JSON file."""
    path = Path(output_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(format_color(f"Results exported to {path}", "green"))


def export_markdown(results, output_path, show_full=False, show_context=False, duration=None):
    """Generate a Markdown report from results."""
    grouped = results.get("grouped", {})
    all_findings = results.get("all", [])

    lines = []
    lines.append('# JSX Scan Report')
    lines.append('')
    lines.append(f'*Generated: {datetime.utcnow().isoformat()} UTC*')
    if duration is not None:
        lines.append(f'*Scan duration: {duration:.2f}s*')
    lines.append('')

    lines.append('## Summary')
    lines.append('')
    for k, v in grouped.items():
        lines.append(f'- **{k}**: {len(v)}')
    lines.append('')

    sev_counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for f in all_findings:
        sev_counts[f.get('severity', 'info')] = sev_counts.get(f.get('severity', 'info'), 0) + 1

    lines.append('### By severity')
    lines.append('')
    lines.append(f"- High: {sev_counts.get('high',0)}")
    lines.append(f"- Medium: {sev_counts.get('medium',0)}")
    lines.append(f"- Low: {sev_counts.get('low',0)}")
    lines.append('')

    lines.append('## Findings')
    lines.append('')
    for detector_name, findings in grouped.items():
        if not findings:
            continue
        lines.append(f'### {detector_name}')
        lines.append('')
        for f in findings:
            raw = f.get('value')
            display = normalize_value(raw)
            if not show_full:
                display = mask_value(display, show_full=False)
            occ = f.get('occurrences', 1)
            lines.append(f'- **{display}**  ')
            lines.append(f'  - Detector: {f.get("detector")}  ')
            lines.append(f'  - Severity: {f.get("severity")}  ')
            lines.append(f'  - Occurrences: {occ}  ')
            if f.get('lines'):
                lines.append(f'  - Lines: {", ".join(str(l) for l in f.get("lines"))}  ')
            lines.append(f'  - Confidence: {f.get("confidence",0)}%  ')
            if show_context and f.get('context'):
                ctx = f.get('context')
                lines.append(f'  - Context: `{ctx}`  ')
        lines.append('')

    with open(output_path, 'w', encoding='utf-8') as md:
        md.write('\n'.join(lines))


def export_html(results, output_path, show_full=False, show_context=False, duration=None):
    """Generate a simple HTML report from results."""
    grouped = results.get("grouped", {})
    all_findings = results.get("all", [])

    def esc(s):
        return html_escape.escape(str(s))

    html_lines = []
    html_lines.append('<!doctype html>')
    html_lines.append('<html><head><meta charset="utf-8"><title>JSX Scan Report</title>')
    html_lines.append('<style>body{font-family:Arial,Helvetica,sans-serif;padding:20px}h1,h2,h3{color:#222}pre{background:#f5f5f5;padding:10px;overflow:auto}</style>')
    html_lines.append('</head><body>')
    html_lines.append('<h1>JSX Scan Report</h1>')
    html_lines.append(f'<p><em>Generated: {esc(datetime.utcnow().isoformat())} UTC</em></p>')
    if duration is not None:
        html_lines.append(f'<p><em>Scan duration: {duration:.2f}s</em></p>')

    html_lines.append('<h2>Summary</h2>')
    html_lines.append('<ul>')
    for k, v in grouped.items():
        html_lines.append(f'<li><strong>{esc(k)}</strong>: {len(v)}</li>')
    html_lines.append('</ul>')

    html_lines.append('<h3>By severity</h3><ul>')
    sev_counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for f in all_findings:
        sev_counts[f.get('severity', 'info')] = sev_counts.get(f.get('severity', 'info'), 0) + 1
    html_lines.append(f'<li>High: {sev_counts.get('"'"'high'"'"',0)}</li>')
    html_lines.append(f'<li>Medium: {sev_counts.get('"'"'medium'"'"',0)}</li>')
    html_lines.append(f'<li>Low: {sev_counts.get('"'"'low'"'"',0)}</li>')
    html_lines.append('</ul>')

    html_lines.append('<h2>Findings</h2>')
    for detector_name, findings in grouped.items():
        if not findings:
            continue
        html_lines.append(f'<h3>{esc(detector_name)}</h3>')
        html_lines.append('<ul>')
        for f in findings:
            raw = f.get('value')
            display = normalize_value(raw)
            if not show_full:
                display = mask_value(display, show_full=False)
            html_lines.append('<li>')
            html_lines.append(f'<strong>{esc(display)}</strong>')
            html_lines.append('<ul>')
            html_lines.append(f'<li>Detector: {esc(f.get("detector"))}</li>')
            html_lines.append(f'<li>Severity: {esc(f.get("severity"))}</li>')
            html_lines.append(f'<li>Occurrences: {esc(f.get("occurrences",1))}</li>')
            if f.get('lines'):
                html_lines.append(f'<li>Lines: {esc(", ".join(str(l) for l in f.get("lines")))}</li>')
            html_lines.append(f'<li>Confidence: {esc(f.get("confidence",0))}%</li>')
            if show_context and f.get('context'):
                html_lines.append(f'<li>Context: <pre>{esc(f.get("context"))}</pre></li>')
            html_lines.append('</ul>')
            html_lines.append('</li>')
        html_lines.append('</ul>')

    html_lines.append('</body></html>')

    with open(output_path, 'w', encoding='utf-8') as hf:
        hf.write('\n'.join(html_lines))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="JSX - JavaScript Secret Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n  python JSX.py --file ./script.js\n  python JSX.py --url https://example.com/app.js\n  python JSX.py --file ./script.js --json results.json"
    )

    parser.add_argument("-f", "--file", help="Local JavaScript file to scan")
    parser.add_argument("-u", "--url", help="Remote JavaScript file URL to scan")
    parser.add_argument("-j", "--json", help="Export results to JSON file", dest="json_output")
    parser.add_argument("--context", action="store_true", help="Show surrounding code context for each finding")
    parser.add_argument("--show-full", action="store_true", help="Show full secret values (do not mask)")
    parser.add_argument("--summary-only", action="store_true", help="Show only the summary of the scan")
    parser.add_argument("--severity", choices=["low", "medium", "high", "info"], help="Filter findings by severity")
    parser.add_argument("--detector", help="Filter findings by detector name (exact match)")
    parser.add_argument("--report-md", help="Export a Markdown report to the given file path")
    parser.add_argument("--report-html", help="Export an HTML report to the given file path")

    args = parser.parse_args()

    try:
        if not args.file and not args.url:
            parser.print_help(sys.stderr)
            print(format_color("\nError: specify --file or --url", "red"), file=sys.stderr)
            return 1

        import time

        banner = """
JJJJJ  SSSSS  X   X
    J  S      X X X
    J   SSS    X X 
J   J      S   X X 
 JJJ   SSSSS  X   X

JavaScript Secret by Xerog
JSX v0.2.0
"""
        print(format_color(banner, "cyan"), file=sys.stderr)

        print("Loading content...", file=sys.stderr)
        content = load_content(args.file, args.url)
        print(format_color("Content loaded", "green"), file=sys.stderr)

        file_size = None
        try:
            if args.file:
                file_size = Path(args.file).stat().st_size
        except Exception:
            file_size = None

        print("Scanning content...", file=sys.stderr)
        start = time.perf_counter()
        scanner = Scanner()
        results = scanner.scan(content)
        duration = time.perf_counter() - start
        print(format_color(f"Scan complete ({duration:.2f}s)", "green"), file=sys.stderr)

        if args.json_output:
            export_json(results, args.json_output)

        grouped = results.get("grouped", {})
        all_findings = results.get("all", [])

        if args.detector:
            grouped = {k: v for k, v in grouped.items() if k.lower() == args.detector.lower()}
        if args.severity:
            for k in list(grouped.keys()):
                grouped[k] = [f for f in grouped[k] if f.get("severity") == args.severity]

        if args.summary_only:
            counts_by_type = {k: len(v) for k, v in grouped.items()}
            counts_by_sev = {"high": 0, "medium": 0, "low": 0, "info": 0}
            for f in all_findings:
                sev = f.get("severity", "info")
                counts_by_sev[sev] = counts_by_sev.get(sev, 0) + 1

            print("\nScan Summary\n")
            for k, c in sorted(counts_by_type.items(), key=lambda x: x[0].lower()):
                print(f"{k:20} {c}")
            print("")

        if args.report_md:
            try:
                export_markdown(results, args.report_md, show_full=args.show_full, show_context=args.context, duration=duration)
                print(format_color(f"Markdown report saved to {args.report_md}", "green"))
            except Exception as e:
                print(format_color(f"Failed to write markdown report: {e}", "red"))

        if args.report_html:
            try:
                export_html(results, args.report_html, show_full=args.show_full, show_context=args.context, duration=duration)
                print(format_color(f"HTML report saved to {args.report_html}", "green"))
            except Exception as e:
                print(format_color(f"Failed to write HTML report: {e}", "red"))


        print("")
        for detector_name, findings in grouped.items():
            if not findings:
                continue
            print(format_color(detector_name, "underline"))
            for f in findings:
                val = f.get("value")
                display_val = normalize_value(val)
                masked = mask_value(display_val, show_full=args.show_full)
                if not args.show_full and isinstance(masked, str) and len(masked) > 80:
                    masked = masked[:77] + '...'
                occ = f.get("occurrences", 1)
                lines = f.get("lines", [])
                conf = f.get("confidence", 0)
                sev = f.get("severity", "info")

                sev_color = {"high": "red", "medium": "yellow", "low": "cyan", "info": "cyan"}.get(sev, "cyan")
                print(f"  {format_color(sev.upper(), sev_color)} {format_color(masked, 'white')} {format_color(f'({occ}x)', 'dim')}")
                if lines:
                    print(f"    Line(s): {', '.join(str(l) for l in lines)}")
                print(f"    Confidence: {conf}%")
                if args.context and f.get("context"):
                    ctx = f.get('context')
                    if isinstance(ctx, str) and len(ctx) > 300:
                        ctx = ctx[:300] + '...'
                    print(format_color(f"    Context: {ctx}", "dim"))
            print("")

        return 0

    except Exception as e:
        print(format_color(f"Error: {e}", "red"), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
