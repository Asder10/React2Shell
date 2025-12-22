"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from react2shell.utils.config import Config
from react2shell.core.scanner import Scanner
from react2shell.ui.console import console
from react2shell.ui.reporting import Reporter

def run_scanner(config: Config):
    if not config.list_file:
        console.print("[error][!] No host list provided.[/error]")
        return

    from react2shell.utils.helpers import parse_host_list, normalize_url
    hosts = [normalize_url(h) for h in parse_host_list(config.list_file)]
    
    if not hosts:
        console.print("[error][!] Host list is empty or file not found.[/error]")
        return

    console.print(f"[info][*] Starting scan on {len(hosts)} targets with {config.threads} threads...[/info]")
    
    results = []
    scanner = Scanner(config)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Scanning...", total=len(hosts))
        
        with ThreadPoolExecutor(max_workers=config.threads) as executor:
            futures = {executor.submit(scanner.scan_target, host): host for host in hosts}
            for future in as_completed(futures):
                res = future.result()
                results.append(res)
                if res["vulnerable"]:
                    console.print(f"[success][VULNERABLE][/success] [highlight]{res['host']}[/highlight]")
                    if res["output"]:
                        console.print(f"   [dim]→ Output: {res['output']}[/dim]")
                elif config.verbose:
                    console.print(f"[dim][NOT VULNERABLE] {res['host']}[/dim]")
                
                progress.update(task, advance=1)

    # Reporting
    if config.output_file:
        if config.output_file.endswith(".json"):
            Reporter.save_json(results, config.output_file)
        elif config.output_file.endswith(".csv"):
            Reporter.save_csv(results, config.output_file)
        else:
            Reporter.save_html(results, config.output_file)
    
    vuln_count = sum(1 for r in results if r["vulnerable"])
    console.print(f"\n[info][*] Scan finished. Found [error]{vuln_count}[/error] vulnerable targets.[/info]")
