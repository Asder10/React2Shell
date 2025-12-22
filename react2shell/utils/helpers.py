"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
import random
import string
from urllib.parse import urlparse

def generate_random_string(length: int = 8) -> str:
    """Generate a random string of fixed length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def normalize_url(url: str) -> str:
    """Normalize URL to include scheme if missing."""
    url = url.strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url.rstrip("/")

def parse_host_list(file_path: str) -> list[str]:
    """Parse a file of hosts, ignoring comments and empty lines."""
    hosts = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    hosts.append(line)
    except Exception:
        pass 
    return hosts
