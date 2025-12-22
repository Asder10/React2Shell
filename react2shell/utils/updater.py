"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
import subprocess
import sys
import os
from react2shell.ui.console import console

def check_for_updates():
    """Checks for updates using git and performs a pull if requested."""
    console.print("[info][*] Checking for updates...[/info]")
    
    try:
        # Check if it's a git repo
        if not os.path.exists(".git"):
            console.print("[warning][!] Not a git repository. Manual update required.[/warning]")
            return

        # Fetch latest
        subprocess.run(["git", "fetch"], capture_output=True, check=True)
        
        # Check if local is behind remote
        local = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        remote = subprocess.check_output(["git", "rev-parse", "@{u}"]).decode().strip()
        
        if local != remote:
            console.print("[success][+] Update available![/success]")
            if console.input("[question] Do you want to update now? (y/N): [/question]").lower() == 'y':
                console.print("[info][*] Updating...[/info]")
                subprocess.run(["git", "pull"], check=True)
                console.print("[success][+] Updated successfully! Please restart the tool.[/success]")
                sys.exit(0)
        else:
            console.print("[info][*] You are running the latest version.[/info]")
            
    except subprocess.CalledProcessError:
        console.print("[error][!] Failed to check for updates. Make sure git is installed and configured.[/error]")
    except Exception as e:
        console.print(f"[error][!] Error during update: {e}[/error]")

if __name__ == "__main__":
    check_for_updates()
