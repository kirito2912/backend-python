import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict
from dotenv import load_dotenv

def _load_env():
    load_dotenv()
    env_path = os.path.join(os.path.dirname(__file__), "config.env")
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)

def _request(method: str, base_url: str, path: str, token: Optional[str] = None, data: Optional[Dict] = None):
    if not path.startswith("/"):
        path = "/" + path
    url = base_url.rstrip("/") + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            if content:
                return json.loads(content)
            return None
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8")
        except Exception:
            detail = str(e)
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {detail}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Error de conexión: {e.reason}. Verifica 'API_BASE_URL' y que el servidor esté accesible.")

def api_get(base_url: str, path: str, token: Optional[str] = None):
    return _request("GET", base_url, path, token=token)

def api_post(base_url: str, path: str, token: Optional[str] = None, data: Optional[Dict] = None):
    return _request("POST", base_url, path, token=token, data=data)

def main():
    _load_env()
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default="/api/resultados/presidencial")
    parser.add_argument("--method", type=str, choices=["GET", "POST"], default="GET")
    parser.add_argument("--data", type=str, default=None)
    parser.add_argument("--base-url", type=str, default=os.getenv("API_BASE_URL", "http://localhost:8000"))
    parser.add_argument("--token", type=str, default=os.getenv("API_TOKEN"))
    args = parser.parse_args()

    payload = None
    if args.data:
        try:
            payload = json.loads(args.data)
        except json.JSONDecodeError as e:
            raise SystemExit(f"JSON inválido en --data: {e}")

    try:
        if args.method == "GET":
            result = api_get(args.base_url, args.path, args.token)
        else:
            result = api_post(args.base_url, args.path, args.token, payload)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        raise SystemExit(str(e))

if __name__ == "__main__":
    main()

