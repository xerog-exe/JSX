"""Command-line interface for JSX scanner."""

import argparse
import json
import sys
import re
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

    # JWT-like: contain two dots and long
    try:
        if value.count('.') == 2 and len(value) > 20:
            return value[:24] + '...'
    except Exception:
        pass

    # Google API key
    if isinstance(value, str) and value.startswith('AIza') and len(value) > 10:
        return value[:4] + '*' * (len(value) - 8) + value[-4:]

    # AWS key
    if isinstance(value, str) and value.startswith('AKIA') and len(value) >= 16:
        return value[:4] + '*' * (len(value) - 8) + value[-4:]

    # Generic long secret
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

    # token patterns to try in priority order
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

    # fallback: return first 120 chars
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

    args = parser.parse_args()

    try:
        # Validate arguments
        if not args.file and not args.url:
            parser.print_help(sys.stderr)
            print(format_color("\nError: specify --file or --url", "red"), file=sys.stderr)
            return 1

        import time

        # Banner
        banner = """
██████╗ ███████╗██╗  ██╗
██╔══██╗██╔════╝╚██╗██╔╝
██████╔╝███████╗ ╚███╔╝
██╔══██╗╚════██║ ██╔██╗
██║  ██║███████║██╔╝ ██╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

JavaScript Secret by Xerog
v0.2.0
"""
        print(format_color(banner, "cyan"), file=sys.stderr)

        # Load content
        print("Loading content...", file=sys.stderr)
        content = load_content(args.file, args.url)
        print(format_color("Content loaded", "green"), file=sys.stderr)

        # File metadata
        file_size = None
        try:
            if args.file:
                file_size = Path(args.file).stat().st_size
        except Exception:
            file_size = None

        # Scan
        print("Scanning content...", file=sys.stderr)
        start = time.perf_counter()
        scanner = Scanner()
        results = scanner.scan(content)
        duration = time.perf_counter() - start
        print(format_color(f"Scan complete ({duration:.2f}s)", "green"), file=sys.stderr)

        # Optionally export JSON
        if args.json_output:
            export_json(results, args.json_output)

        # Prepare summary data
        grouped = results.get("grouped", {})
        all_findings = results.get("all", [])

        # Apply filters
        if args.detector:
            grouped = {k: v for k, v in grouped.items() if k.lower() == args.detector.lower()}
        if args.severity:
            for k in list(grouped.keys()):
                grouped[k] = [f for f in grouped[k] if f.get("severity") == args.severity]

        # Summary only
        if args.summary_only:
            # Build summary
            counts_by_type = {k: len(v) for k, v in grouped.items()}
            counts_by_sev = {"high": 0, "medium": 0, "low": 0, "info": 0}
            for f in all_findings:
                sev = f.get("severity", "info")
                counts_by_sev[sev] = counts_by_sev.get(sev, 0) + 1

            print("\nScan Summary\n")
            for k, c in sorted(counts_by_type.items(), key=lambda x: x[0].lower()):
                print(f"{k:20} {c}")
            print("")
            print(f"High Severity       {counts_by_sev.get('high',0)}")
            print(f"Medium Severity     {counts_by_sev.get('medium',0)}")
            print(f"Low Severity        {counts_by_sev.get('low',0)}")
            print(f"Scan Time           {duration:.2f} sec")
            return 0

        # Print detailed results with masking by default
        print("")
        for detector_name, findings in grouped.items():
            if not findings:
                continue
            print(format_color(detector_name, "underline"))
            for f in findings:
                val = f.get("value")
                # Normalize large detector values that may contain full JSON blobs
                display_val = normalize_value(val)
                masked = mask_value(display_val, show_full=args.show_full)
                # Truncate for display if not showing full
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
