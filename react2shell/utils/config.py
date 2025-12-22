"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
import argparse
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Config:
    url: Optional[str] = None
    list_file: Optional[str] = None
    threads: int = 10
    timeout: int = 10
    output_file: Optional[str] = None
    verbose: bool = False
    insecure: bool = True
    headers: List[str] = field(default_factory=list)
    proxy: Optional[str] = None
    
    # Modes
    shell: bool = False
    check: bool = False  # Safe check
    stealth: bool = False
    wizard: bool = False
    update: bool = False
    
    # WAF & Evasion
    waf_bypass: bool = False
    waf_size: int = 128
    obfuscate: bool = False
    
    # Payloads
    windows: bool = False
    command: Optional[str] = None

def parse_args() -> Config:
    parser = argparse.ArgumentParser(description="React2Shell - Advanced CVE-2025-55182 Exploitation Framework")
    
    # Target Selection
    target_group = parser.add_argument_group("Target Selection")
    target_group.add_argument("-u", "--url", help="Single target URL")
    target_group.add_argument("-l", "--list", help="File containing list of targets")
    
    # Modes
    mode_group = parser.add_argument_group("Modes")
    mode_group.add_argument("--shell", action="store_true", help="Start interactive shell")
    mode_group.add_argument("--check", action="store_true", help="Safe vulnerability check (no RCE)")
    mode_group.add_argument("--wizard", action="store_true", help="Start interactive Wizard mode")
    mode_group.add_argument("--update", action="store_true", help="Check for tool updates")
    
    # Options
    opt_group = parser.add_argument_group("Options")
    opt_group.add_argument("-t", "--threads", type=int, default=10, help="Number of threads")
    opt_group.add_argument("--timeout", type=int, default=10, help="Request timeout")
    opt_group.add_argument("-o", "--output", help="Output file (JSON/HTML)")
    opt_group.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    opt_group.add_argument("-k", "--insecure", action="store_true", default=True, help="Ignore SSL errors")
    opt_group.add_argument("-H", "--header", action="append", dest="headers", help="Custom headers")
    opt_group.add_argument("--proxy", help="Proxy URL (http:// or socks5://)")
    
    # Advanced
    adv_group = parser.add_argument_group("Advanced / Evasion")
    adv_group.add_argument("--stealth", action="store_true", help="Enable stealth mode (random delays, UA rotation)")
    adv_group.add_argument("--waf-bypass", action="store_true", help="Enable WAF bypass (junk data)")
    adv_group.add_argument("--waf-size", type=int, default=128, help="Junk data size in KB")
    adv_group.add_argument("--obfuscate", action="store_true", help="Obfuscate payload")
    adv_group.add_argument("--windows", action="store_true", help="Use Windows payloads")
    adv_group.add_argument("-c", "--command", help="Execute single command")

    args = parser.parse_args()
    
    return Config(
        url=args.url,
        list_file=args.list,
        threads=args.threads,
        timeout=args.timeout,
        output_file=args.output,
        verbose=args.verbose,
        insecure=args.insecure,
        headers=args.headers or [],
        proxy=args.proxy,
        shell=args.shell,
        check=args.check,
        stealth=args.stealth,
        wizard=args.wizard,
        waf_bypass=args.waf_bypass,
        waf_size=args.waf_size,
        obfuscate=args.obfuscate,
        windows=args.windows,
        command=args.command,
        update=args.update
    )
