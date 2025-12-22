"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
import sys
from react2shell.utils.config import parse_args
from react2shell.ui.banner import print_banner
from react2shell.ui.console import console

def main():
    config = parse_args()
    
    print_banner()
    
    if config.update:
        from react2shell.utils.updater import check_for_updates
        check_for_updates()
        return

    try:
        if config.shell:
            from react2shell.modules.shell_module import run_shell
            run_shell(config)
        elif config.list_file:
            from react2shell.modules.scanner_module import run_scanner
            run_scanner(config)
        elif config.url:
            from react2shell.core.scanner import Scanner
            scanner = Scanner(config)
            res = scanner.scan_target(config.url)
            if res["vulnerable"]:
                console.print(f"[success][VULNERABLE][/success] [highlight]{res['host']}[/highlight]")
                if res["output"]:
                    console.print(f"   [dim]→ Output: {res['output']}[/dim]")
            else:
                console.print(f"[error][SAFE][/error] [dim]{res['host']}[/dim]")
        elif config.wizard:
            console.print("[info][*] Wizard mode coming soon...[/info]")
        else:
            console.print("[warning][!] No action specified. Use -h for help.[/warning]")
            
    except KeyboardInterrupt:
        console.print("\n[info][*] Interrupted by user. Exiting...[/info]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[error][!] Fatal error: {e}[/error]")
        if config.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
