"""Command-line interface for JSX scanner."""

import argparse
import json
import sys
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


def print_results(results):
    """Print results in a formatted, colored manner."""
    grouped = results.get("grouped", {})

    # Filter categories with findings
    categories = [k for k, v in grouped.items() if v]

    if not categories:
        print(format_color("\nNo findings detected.", "green"))
        return

    print("")
    for category in categories:
        findings = grouped[category]
        print(format_color(format_color(category, "bold"), "underline"))

        for finding in findings:
            severity = finding.get("severity", "info")
            value = finding.get("value", "")
            context = finding.get("context", "")

            # Color by severity
            sev_color = {
                "high": "red",
                "medium": "yellow",
                "low": "cyan",
                "info": "cyan",
            }.get(severity, "cyan")

            sev_text = format_color(severity.upper(), sev_color)
            value_text = format_color(value, "white")

            print(f"  {sev_text} {value_text}")
            if context:
                context_text = format_color(context[:100], "dim")
                print(f"    {context_text}")

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

    args = parser.parse_args()

    try:
        # Validate arguments
        if not args.file and not args.url:
            parser.print_help(sys.stderr)
            print(format_color("\nError: specify --file or --url", "red"), file=sys.stderr)
            return 1

        # Load content
        print("Loading content...", file=sys.stderr)
        content = load_content(args.file, args.url)
        print(format_color("Content loaded", "green"), file=sys.stderr)

        # Scan
        print("Scanning content...", file=sys.stderr)
        scanner = Scanner()
        results = scanner.scan(content)
        print(format_color("Scan complete", "green"), file=sys.stderr)

        # Print results
        print_results(results)

        # Export JSON if requested
        if args.json_output:
            export_json(results, args.json_output)

        return 0

    except Exception as e:
        print(format_color(f"Error: {e}", "red"), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
