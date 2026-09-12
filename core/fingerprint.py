import httpx

BOT_SIGNATURES = [
    "googlebot", "bingbot", "yahoo", "baidu", "duckduckbot", 
    "slurp", "spider", "crawler", "bot", "curl", "python-requests", 
    "wget", "lighthouse", "pagespeed", "scanner"
]

def is_bot(user_agent: str) -> bool:
    if not user_agent:
        return True
    ua_lower = user_agent.lower()
    for sig in BOT_SIGNATURES:
        if sig in ua_lower:
            return True
    return False

def parse_user_agent(ua_string: str) -> dict:
    ua_lower = ua_string.lower()
    
    os_info = "Unknown OS"
    if "windows" in ua_lower:
        os_info = "Windows"
    elif "android" in ua_lower:
        os_info = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower or "ios" in ua_lower:
        os_info = "iOS"
    elif "mac os" in ua_lower or "macintosh" in ua_lower:
        os_info = "MacOS"
    elif "linux" in ua_lower:
        os_info = "Linux"

    # Browser Detection
    browser_info = "Unknown Browser"
    if "chrome" in ua_lower and "chromium" not in ua_lower and "edg" not in ua_lower:
        browser_info = "Google Chrome"
    elif "firefox" in ua_lower:
        browser_info = "Mozilla Firefox"
    elif "safari" in ua_lower and "chrome" not in ua_lower:
        browser_info = "Apple Safari"
    elif "edg" in ua_lower:
        browser_info = "Microsoft Edge"
    elif "opera" in ua_lower or "opr" in ua_lower:
        browser_info = "Opera"

    # Device Type
    device_type = "Desktop"
    if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
        device_type = "Mobile"
    elif "ipad" in ua_lower or "tablet" in ua_lower:
        device_type = "Tablet"

    return {
        "os": os_info,
        "browser": browser_info,
        "device": device_type
    }

async def get_ip_geolocation(ip_address: str) -> dict:
    if ip_address in ["127.0.0.1", "localhost", "::1"] or ip_address.startswith("192.168.") or ip_address.startswith("10."):
        return {"country": "Local Network", "isp": "Localhost / LAN"}
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"http://ip-api.com/json/{ip_address}")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return {
                        "country": data.get("country", "Unknown"),
                        "isp": data.get("isp", "Unknown")
                    }
    except Exception:
        pass
    
    return {"country": "Unknown", "isp": "Unknown"}