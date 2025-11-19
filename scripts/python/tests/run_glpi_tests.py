import os
import json
import subprocess
import requests

def read_env_envfile():
    env_path = os.path.join(os.getcwd(), '.env')
    vals = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    vals[k.strip()] = v.strip()
    return vals

def init_session(glpi_url, app_token, user_token):
    headers = {
        'App-Token': app_token,
        'Authorization': f'user_token {user_token}',
        'Content-Type': 'application/json'
    }
    r = requests.get(f'{glpi_url}/initSession', headers=headers, timeout=30)
    if r.status_code == 200:
        data = r.json()
        return data.get('session_token')
    raise RuntimeError(f'initSession failed: {r.status_code}')

def kill_session(glpi_url, app_token, session_token):
    headers = {
        'App-Token': app_token,
        'Session-Token': session_token,
        'Content-Type': 'application/json'
    }
    try:
        requests.get(f'{glpi_url}/killSession', headers=headers, timeout=30)
    except Exception:
        pass

def run_py(path, env):
    p = subprocess.Popen(['python', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out, err = p.communicate()
    return p.returncode, out.decode('utf-8', errors='ignore'), err.decode('utf-8', errors='ignore')

def main():
    vals = read_env_envfile()
    glpi_url = vals.get('GLPI_URL', '')
    app_token = vals.get('GLPI_APP_TOKEN', '')
    user_token = vals.get('GLPI_USER_TOKEN', '')
    if not all([glpi_url, app_token, user_token]):
        print(json.dumps({'ok': False, 'reason': 'missing_env_file_values'}))
        return
    try:
        session_token = init_session(glpi_url, app_token, user_token)
    except Exception as e:
        print(json.dumps({'ok': False, 'reason': 'init_session_failed', 'error': str(e)}))
        return
    env = os.environ.copy()
    env['GLPI_API_URL'] = glpi_url
    env['APP_TOKEN'] = app_token
    env['SESSION_TOKEN'] = session_token
    results = {}
    for test in [
        os.path.join('tests', 'test_core_contracts.py'),
        os.path.join('tests', 'test_extended_contracts.py'),
        os.path.join('tests', 'test_task_document_kb_problem_change.py')
    ]:
        code, out, err = run_py(test, env)
        results[os.path.basename(test)] = {'code': code, 'out': out.strip(), 'err': err.strip()[:200]}
    kill_session(glpi_url, app_token, session_token)
    print(json.dumps({'ok': True, 'results': results}, ensure_ascii=False))

if __name__ == '__main__':
    main()