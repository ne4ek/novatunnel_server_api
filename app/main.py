from vump_grpc_client import VUMPClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
import json
import requests

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
API_URL=os.getenv("API_URL")
HOST=os.getenv("HOST")
print(f"{SERVER_TOKEN=}")


v2ray_client = VUMPClient(V2RAY_API_HOST, V2RAY_API_PORT)
inbound_tag = 'inbound'


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


payload = {
    "host": HOST,
    "token": SERVER_TOKEN
}

response = requests.post(API_URL + "/getAllActiveClient", json=payload)

data = response.json()

if response.status_code == 200:
    if data["token"] == SERVER_TOKEN:
        for client in data["clients"]:
            add_v2ray_api_client(client["uuid"])
    else:
        print("Bad token", data["token"])
else:
    print("Bad status code", response.status_code)

@app.post("/addClient")
def add_client(client: Client):
    if client.token == SERVER_TOKEN:
        print("new_client", client.uuid)
        # add_v2ray_config_client(client.uuid)
        add_v2ray_api_client(client.uuid)
        return {"message": "Client was added succesfuly!"}
    raise HTTPException(status_code=403, detail="Invalid token")
