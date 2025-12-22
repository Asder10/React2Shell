"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
import json
import csv
from datetime import datetime
from react2shell.ui.console import console

class Reporter:
    @staticmethod
    def save_json(results, output_file):
        data = {
            "tool": "React2Shell",
            "author": "@BlackTechX011",
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        console.print(f"[success][+][/success] Results saved to [highlight]{output_file}[/highlight] (JSON)")

    @staticmethod
    def save_csv(results, output_file):
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["host", "vulnerable", "status_code", "output", "error"])
            writer.writeheader()
            for r in results:
                writer.writerow({
                    "host": r["host"],
                    "vulnerable": r["vulnerable"],
                    "status_code": r["status_code"],
                    "output": r["output"],
                    "error": r["error"]
                })
        console.print(f"[success][+][/success] Results saved to [highlight]{output_file}[/highlight] (CSV)")

    @staticmethod
    def save_html(results, output_file):
        # Basic HTML template
        html_content = f"""
        <html>
        <head>
            <title>React2Shell Report</title>
            <style>
                body {{ font-family: sans-serif; background: #1a1a1a; color: #eee; padding: 20px; }}
                h1 {{ color: #ff4444; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #444; }}
                th {{ background: #333; }}
                .vuln {{ color: #ff4444; font-weight: bold; }}
                .safe {{ color: #00ff00; }}
            </style>
        </head>
        <body>
            <h1>React2Shell Scan Report</h1>
            <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Author: @BlackTechX011</p>
            <table>
                <tr>
                    <th>Host</th>
                    <th>Vulnerable</th>
                    <th>Status</th>
                    <th>Output</th>
                </tr>
        """
        for r in results:
            status_class = "vuln" if r["vulnerable"] else "safe"
            html_content += f"""
                <tr>
                    <td>{r["host"]}</td>
                    <td class="{status_class}">{r["vulnerable"]}</td>
                    <td>{r["status_code"]}</td>
                    <td>{r["output"] or "N/A"}</td>
                </tr>
            """
        html_content += "</table></body></html>"
        with open(output_file, 'w') as f:
            f.write(html_content)
        console.print(f"[success][+][/success] Results saved to [highlight]{output_file}[/highlight] (HTML)")
