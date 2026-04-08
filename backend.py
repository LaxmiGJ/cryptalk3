import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATA_FILE = Path("message_store.json")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessagePayload(BaseModel):
    sender: str
    receiver: str
    encrypted: str
    key: str
    nonce: str
    sender_lang: str
    receiver_lang: str
    emotion: str
    tagged_text: str


def load_storage():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_storage(data):
    DATA_FILE.write_text(json.dumps(data))


@app.post("/send")
def send_message(message: MessagePayload):
    payload = message.dict()
    save_storage(payload)
    return {"status": "stored"}


@app.get("/get")
def get_message():
    storage = load_storage()
    if not storage:
        raise HTTPException(status_code=404, detail="No message stored")
    return storage
