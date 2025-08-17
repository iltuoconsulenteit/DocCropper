import os, json, urllib.request
from fastapi import Request
from fastapi.responses import JSONResponse

__all__ = ["register"]

def load_plugin_settings():
    cfg = {
        "enable_docuseal": False,
        "docuseal_dev_only": True,
        "docuseal_api_url": "",
        "docuseal_api_key": "",
    }
    path = os.path.join(os.path.dirname(__file__), "settings.json")
    if os.path.exists(path):
        try:
            with open(path) as fh:
                cfg.update(json.load(fh))
        except Exception:
            pass
    env_enable = os.getenv("DOCROPPER_ENABLE_DOCUSEAL")
    if env_enable is not None:
        cfg["enable_docuseal"] = env_enable.lower() == "true"
    env_dev = os.getenv("DOCROPPER_DOCUSEAL_DEV_ONLY")
    if env_dev is not None:
        cfg["docuseal_dev_only"] = env_dev.lower() == "true"
    env_url = os.getenv("DOCUSEAL_API_URL")
    if env_url:
        cfg["docuseal_api_url"] = env_url
    env_key = os.getenv("DOCUSEAL_API_KEY")
    if env_key:
        cfg["docuseal_api_key"] = env_key
    return cfg

def save_plugin_settings(update: dict):
    path = os.path.join(os.path.dirname(__file__), "settings.json")
    current = {}
    if os.path.exists(path):
        try:
            with open(path) as fh:
                current = json.load(fh)
        except Exception:
            pass
    current.update(update)
    with open(path, "w") as fh:
        json.dump(current, fh, indent=2)


def register(app, utils):
    get_session_dir = utils["get_session_dir"]
    decrypt_file = utils["decrypt_file"]
    ENC_SUFFIX = utils["ENC_SUFFIX"]

    @app.post('/docuseal-sign/')
    async def docuseal_sign(request: Request):
        settings = load_plugin_settings()
        if not settings.get("enable_docuseal"):
            return JSONResponse(status_code=404, content={'message': 'Docuseal disabled'})
        session_id = request.cookies.get('session_id')
        session_dir = get_session_dir(session_id)
        pdf_path = os.path.join(session_dir, 'output.pdf' + ENC_SUFFIX)
        if not os.path.exists(pdf_path):
            return JSONResponse(status_code=404, content={'message': 'PDF not found'})
        api_url = settings.get('docuseal_api_url')
        api_key = settings.get('docuseal_api_key')
        if not api_url or not api_key:
            return JSONResponse(status_code=400, content={'message': 'Docuseal not configured'})
        try:
            data = decrypt_file(session_id, pdf_path)
            if data is None:
                return JSONResponse(status_code=500, content={'message': 'Decrypt failed'})
            req = urllib.request.Request(api_url, data=data, method='POST')
            req.add_header('Authorization', f'Bearer {api_key}')
            req.add_header('Content-Type', 'application/pdf')
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = resp.read()
            resp_json = json.loads(resp_data.decode())
            url = resp_json.get('url') or resp_json.get('sign_url')
            if not url:
                raise ValueError('no url')
            return {'url': url}
        except Exception:
            return JSONResponse(status_code=500, content={'message': 'Docuseal request failed'})
