from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from chain_append import call_chain 
import json
import os
import requests
import base64
from io import BytesIO
from PIL import Image

app = FastAPI()

# Load from environment or hardcode for testing
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "token")

app = FastAPI()

@app.get("/webhook", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return hub_challenge
    else:
        raise HTTPException(status_code=403, detail="Verification token mismatch")

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    print("🔔 Webhook received:")
    images = []
    try:
        photos = data["entry"][0]["changes"][0]["value"]['photos']
        for p in range(len(photos)):
            img_link = photos[p]
            base_64 = to_base(img_link)
            json_string = json.dumps(data)
            json_dict = json.loads(json_string) 
            images.append(base_64)
            json_dict[f'image64'] =  images
            data = json_dict
            
    except Exception as e:
        print(e)

    try: 
        img_link = data["entry"][0]["changes"][0]["value"]["link"]
        base_64 = to_base(img_link)
        json_string = json.dumps(data)
        json_dict = json.loads(json_string) 
        images.append(base_64)
        json_dict[f'image64'] =  images
        data = json_dict

    except Exception as e:   
        print(e)

    payload = {"json": data}
    
    key = payload['json']['entry'][0]['changes'][0]['value']['post_id']
    stream = payload['json']['entry'][0]['changes'][0]['value']['from']['name'] + "_" + payload['json']['entry'][0]['id']    
    call_chain('create', ['stream' , stream, False])
    call_chain('subscribe', [stream])
    call_chain('publishfrom', ['1WwHjZoF3ozuSgmhrdSMJubKLmapdTr5V6L83C' , stream, key, payload])

    return {"status": "received"}


def to_base(img_link):
    response = requests.get(img_link)
    img = Image.open(BytesIO(response.content))
    
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    buffer = BytesIO()
    img.save(buffer, format="WEBP")
    base_64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return base_64
