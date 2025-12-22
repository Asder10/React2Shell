"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from react2shell.ui.console import console

import platform
import sys

def print_banner():
    """Prints the React2Shell banner."""
    banner_text = """
    ██████╗ ███████╗ █████╗  ██████╗████████╗██████╗ ███████╗██╗  ██╗███████╗██╗     ██╗     
    ██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝╚════██╗██╔════╝██║  ██║██╔════╝██║     ██║     
    ██████╔╝█████╗  ███████║██║        ██║    █████╔╝███████╗███████║█████╗  ██║     ██║     
    ██╔══██╗██╔══╝  ██╔══██║██║        ██║   ██╔═══╝ ╚════██║██╔══██║██╔══╝  ██║     ██║     
    ██║  ██║███████╗██║  ██║╚██████╗   ██║   ███████╗███████║██║  ██║███████╗███████╗███████╗
    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
    """
    
    version = "1.0.0"
    author = "@BlackTechX011"
    
    info_text = Text()
    info_text.append(f"v{version}", style="bold green")
    info_text.append(" | ", style="white")
    info_text.append(author, style="bold cyan")
    info_text.append(" | ", style="white")
    info_text.append(f"{platform.system()} {platform.release()}", style="dim yellow")
    
    subtitle = Text("\n\nNext.js / React Server Functions RCE Framework", style="italic white")
    
    from rich.console import Group
    
    panel = Panel(
        Align.center(
            Group(
                Align.center(Text(banner_text, style="bold red")),
                Align.center(info_text),
                Align.center(subtitle)
            )
        ),
        border_style="red",
        padding=(1, 2),
        title="[bold white]React2Shell[/bold white]",
        title_align="left",
    )
    console.print(panel)
