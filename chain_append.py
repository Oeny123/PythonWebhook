import requests, json, configparser
import os

rpc_config = configparser.ConfigParser()
rpc_config.read('config.ini')
headers = {'content-type': 'application/json'}

connections = {}
try:
    rpc_local = rpc_config['chain1']['datadir']
    rpc_port = rpc_config['chain1']['port']
    rpc_connect = f"http://127.0.0.1:{rpc_port}/"
    path = os.path.expanduser(rpc_local)
    with open(path) as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                if key == 'rpcuser':
                    user = value
                if key == 'rpcpassword':
                    connections['chain1'] = {
                        'connect' : rpc_connect,
                        'user': user,
                        'password' : value
                    }
except Exception as e:
    print(e)

def call_chain(method, params=[]):
    payload = json.dumps({
        "method": method,
        "params": params,
        "id": 1
    })
    try:
        response = requests.post(connections[f'chain1']['connect'], headers=headers, data=payload, auth=(connections[f'chain1']['user'], connections[f'chain1']['password']))
        if response.status_code == 200 and response.text:
            return response.json()['result']
        else:
            print(f"RPC Message: {response.text}")
              
            return response.status_code
    except requests.exceptions.RequestException as e:
        return e