import subprocess
import time
import re
import shutil

def start_tunnel(port: int, provider: str = "cloudflare") -> str | None:
    if provider == "cloudflare":
        if not shutil.which("cloudflared"):
            print("[-] 'cloudflared' command not found. Please ensure cloudflared is installed.")
            return None
        try:
            process = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            start_time = time.time()
            while time.time() - start_time < 15:
                line = process.stdout.readline()
                if not line:
                    break
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if match:
                    return match.group(0)
        except Exception as e:
            print(f"[-] Cloudflare Tunnel Error: {e}")
            
    elif provider == "localtunnel":
        if not shutil.which("npx"):
            print("[-] 'npx' (Node.js) not found. Please ensure Node.js is installed.")
            return None
        try:
            process = subprocess.Popen(
                ["npx", "localtunnel", "--port", str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            start_time = time.time()
            while time.time() - start_time < 15:
                line = process.stdout.readline()
                if not line:
                    break
                match = re.search(r"https://[a-zA-Z0-9-]+\.loca\.lt", line)
                if match:
                    return match.group(0)
        except Exception as e:
            print(f"[-] Localtunnel Error: {e}")
            
    return None