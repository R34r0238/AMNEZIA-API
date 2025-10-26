# amnezia-api/core.py
import os
import json
import subprocess
from datetime import datetime, timedelta, timezone
from config import get_config
from decode import encode as encode_vpn

EXPIRATIONS_FILE = 'files/expirations.json'

def _load_expirations():
    if not os.path.exists(EXPIRATIONS_FILE):
        return {}
    with open(EXPIRATIONS_FILE) as f:
        data = json.load(f)
        for k, v in data.items():
            if v.get('expiration_time'):
                data[k]['expiration_time'] = datetime.fromisoformat(v['expiration_time']).replace(tzinfo=timezone.utc)
        return data

def _save_expirations(data):
    os.makedirs(os.path.dirname(EXPIRATIONS_FILE), exist_ok=True)
    serializable = {}
    for k, v in data.items():
        serializable[k] = {
            'expiration_time': v['expiration_time'].isoformat() if v.get('expiration_time') else None,
            'traffic_limit': v.get('traffic_limit', "Неограниченно")
        }
    with open(EXPIRATIONS_FILE, 'w') as f:
        json.dump(serializable, f)

def _run_script(script_name, *args):
    cmd = ["./" + script_name] + [str(a) for a in args]
    result = subprocess.run(cmd, cwd=".", capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} failed: {result.stderr}")
    return result.stdout

def create_client_with_options(name: str, duration_days: int = None, traffic_limit: str = "Неограниченно"):
    config = get_config()
    _run_script("newclient.sh", name, config['endpoint'], config['wg_config_file'], config['docker_container'])

    expirations = _load_expirations()
    expiration_time = None
    if duration_days is not None:
        expiration_time = datetime.now(timezone.utc) + timedelta(days=duration_days)
    expirations[name] = {'expiration_time': expiration_time, 'traffic_limit': traffic_limit}
    _save_expirations(expirations)

    conf_path = f"users/{name}/{name}.conf"
    vpn_key = None
    if os.path.exists(conf_path):
        with open(conf_path, 'r') as f:
            vpn_key = encode_vpn(f.read())

    return {
        "name": name,
        "vpn_key": vpn_key,
        "expiration_days": duration_days,
        "traffic_limit": traffic_limit
    }

def delete_client_by_name(name: str):
    from db import get_client_list, deactive_user_db
    clients = get_client_list()
    if not any(c[0] == name for c in clients):
        return False
    success = deactive_user_db(name)
    if success:
        expirations = _load_expirations()
        expirations.pop(name, None)
        _save_expirations(expirations)
        # Удаляем папку
        user_dir = f"users/{name}"
        if os.path.exists(user_dir):
            import shutil
            shutil.rmtree(user_dir)
    return success

def get_client_vpn_key(name: str):
    conf_path = f"users/{name}/{name}.conf"
    if not os.path.exists(conf_path):
        return None
    with open(conf_path, 'r') as f:
        return encode_vpn(f.read())

def list_clients():
    from db import get_client_list
    raw = get_client_list()
    return [{"name": c[0], "public_key": c[1], "allowed_ips": c[2]} for c in raw]