# React2Shell Usage Guide

Detailed explanation of all command-line arguments and features.

## Installation & Setup

### Package Manager
Install globally as a toolkit:
```bash
pip install .
```
Now you can use the `react2shell` command from anywhere.

### Manual Usage
```bash
python -m react2shell [options]
```
- `-u, --url`: Specify a single target URL.
- `-l, --list`: Specify a file containing a list of target URLs (one per line).

## Modes
- `--shell`: Start an interactive RCE shell on a vulnerable target.
- `--check`: Perform a safe side-channel check without executing code.
- `--wizard`: [Coming Soon] Step-by-step interactive setup.

## Performance & Connectivity
- `-t, --threads`: Number of concurrent threads for scanning (default: 10).
- `--timeout`: Request timeout in seconds (default: 10).
- `--proxy`: Use an HTTP or SOCKS proxy (e.g., `http://127.0.0.1:8080`).
- `-k, --insecure`: Disable SSL certificate verification (default behavior).

## Evasion & Stealth
- `--stealth`: Enable randomized delays and rotates User-Agents to avoid rate limiting and detection.
- `--waf-bypass`: Appends a large amount of junk data to the request to bypass WAF content inspection limits.
- `--waf-size`: Size of the junk data in KB (default: 128).
- `--obfuscate`: [Coming Soon] Advanced payload obfuscation.
- `--windows`: Use PowerShell-based payloads for Windows targets.

## Reporting
- `-o, --output`: Save results to a file. Format is determined by extension:
    - `.html`: Professional web report.
    - `.json`: Detailed machine-readable data.
    - `.csv`: Spreadsheet-friendly format.

## Examples

### Stealthy Scan with Proxy
```bash
python -m react2shell -l targets.txt --stealth --proxy http://127.0.0.1:9050 -o results.html
```

### Bypassing WAF on a Single Target
```bash
python -m react2shell -u https://protected-target.com --waf-bypass --waf-size 256 --shell
```
