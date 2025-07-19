from vump_grpc_client import VUMPClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
import json

load_dotenv()
import os

app = FastAPI()

class Client(BaseModel):
    token: str
    uuid: str

V2RAY_API_HOST=os.getenv("V2RAY_API_HOST")
V2RAY_API_PORT=os.getenv("V2RAY_API_PORT")
CONFIG_PATH=os.getenv("CONFIG_PATH")
SERVER_TOKEN=os.getenv("SERVER_TOKEN")
print(f"{SERVER_TOKEN=}")

 

v2ray_client = VUMPClient(V2RAY_API_HOST, V2RAY_API_PORT)
inbound_tag = 'inbound'

@app.post("/addClient")
def add_client(client: Client):
    if client.token == SERVER_TOKEN:
        print("new_client", client.uuid)
        add_v2ray_config_client(client.uuid)
        add_v2ray_api_client(client.uuid)
        return {"message": "Client was added succesfuly!"}
    raise HTTPException(status_code=403, detail="Invalid token")

def add_v2ray_config_client(uuid: str): 
   
    new_client = {
        "id": uuid,
        "email": f"{uuid}@n.t",
        "alterId": 0
    }
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    except json.JSONDecodeError:
        raise ValueError("Config file contains invalid JSON")
    
    vmess_inbound = None
    for inbound in config.get('inbounds', []):
        if inbound.get('protocol') == 'vmess':
            vmess_inbound = inbound
            break
    
    if not vmess_inbound:
        raise ValueError("No vmess inbound found in the config")
    
    if 'settings' not in vmess_inbound:
        vmess_inbound['settings'] = {}
    if 'clients' not in vmess_inbound['settings']:
        vmess_inbound['settings']['clients'] = []
    
    vmess_inbound['settings']['clients'].append(new_client)
    
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        raise IOError(f"Failed to write config file: {str(e)}")
    
    return new_client

def add_v2ray_api_client(uuid: str) -> bool :
    try:
        user = v2ray_client.add_client(inbound_tag, uuid, f"{uuid}@n.t")
        if user:
            print(user)
            return True
        return False
    except Exception as e:
        raise e
        return False
