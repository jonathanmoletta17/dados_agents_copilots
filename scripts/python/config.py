import os

def _read_env():
    vals = {}
    candidates = [
        os.path.join(os.getcwd(), '.env'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),
    ]
    for p in candidates:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        k, v = line.split('=', 1)
                        vals[k.strip()] = v.strip()
            break
    return vals

_env = _read_env()
API_URL = _env.get('GLPI_URL', os.environ.get('GLPI_API_URL', '/apirest.php'))
APP_TOKEN = _env.get('GLPI_APP_TOKEN', os.environ.get('APP_TOKEN', ''))
USER_TOKEN = _env.get('GLPI_USER_TOKEN', os.environ.get('USER_TOKEN', ''))

def _load_user_overrides():
    import json
    paths = [
        os.path.join(os.getcwd(), 'scripts', 'python', 'config_user_overrides.json'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'scripts', 'python', 'config_user_overrides.json')
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
    return {}

USER_OVERRIDES = _load_user_overrides()