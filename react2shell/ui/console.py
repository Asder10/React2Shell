"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
from rich.console import Console
from rich.theme import Theme

# Define an "Elite" theme for ultra-pro look
elite_theme = Theme({
    "info": "bold cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
    "dim": "italic grey50",
    "header": "bold white on red",
    "vuln": "bold blink red",
    "clean": "bold bright_green",
    "target": "bold bright_blue",
})

# Global console instance
console = Console(theme=elite_theme, highlight=True)
