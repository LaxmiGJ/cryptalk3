import streamlit as st
from deep_translator import GoogleTranslator
from transformers import pipeline
import zlib
import os
import time
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

BACKEND_SEND_URL = "https://<YOUR-BACKEND-URL>/send"

st.set_page_config(page_title="CrypTalk Sender", page_icon="📤", layout="centered")
st.title("📤 CrypTalk Sender")
st.caption("Encrypt and send a secure message to the receiver app")

EMOJI_MAP = {
    "joy": "😊",
    "sadness": "😢",
    "anger": "😠",
    "fear": "😨",
    "surprise": "😲",
    "neutral": "😐"
}

LANG_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml"
}

col1, col2 = st.columns(2)
with col1:
    sender_name = st.text_input("Sender Name")
with col2:
    receiver_name = st.text_input("Receiver Name")

sender_lang = st.selectbox("Sender Language", list(LANG_CODES.keys()))
receiver_lang = st.selectbox("Receiver Language", list(LANG_CODES.keys()))

user_text = st.text_area("Enter your message", placeholder="Type your message here…", height=140)

send = st.button("🔐 Send Secure Message")


def compress(text):
    return zlib.compress(text.encode())


def encrypt(data):
    key = AESGCM.generate_key(bit_length=128)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    encrypted = aes.encrypt(nonce, data, None)
    return encrypted.hex(), key.hex(), nonce.hex()


@st.cache_resource
def load_models():
    return pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=1,
    )

emotion_classifier = load_models()

if send:
    if not sender_name.strip() or not receiver_name.strip() or not user_text.strip():
        st.warning("Please enter sender, receiver, and a message.")
    else:
        with st.spinner("Processing secure message..."):
            try:
                text_en = GoogleTranslator(source=LANG_CODES[sender_lang], target="en").translate(user_text)
            except Exception as error:
                st.error(f"Translation failed: {error}")
                st.stop()

            prediction = emotion_classifier(text_en)[0][0]
            emotion = prediction["label"]
            emoji = EMOJI_MAP.get(emotion, "💬")
            tagged_text = f"[{emotion.upper()} {emoji}] {text_en}"

            compressed = compress(tagged_text)
            encrypted_hex, key_hex, nonce_hex = encrypt(compressed)

            payload = {
                "sender": sender_name,
                "receiver": receiver_name,
                "encrypted": encrypted_hex,
                "key": key_hex,
                "nonce": nonce_hex,
                "sender_lang": sender_lang,
                "receiver_lang": receiver_lang,
                "emotion": f"{emotion.upper()} {emoji}",
                "tagged_text": tagged_text,
            }

            try:
                response = requests.post(BACKEND_SEND_URL, json=payload, timeout=15)
                response.raise_for_status()
            except requests.RequestException as error:
                st.error(f"Failed to send message: {error}")
                st.stop()

            st.success("✅ Secure message sent to the cloud backend")
            st.markdown("---")
            st.write("**Sender:**", sender_name)
            st.write("**Receiver:**", receiver_name)
            st.write("**Emotion:**", emotion.upper(), emoji)
            st.write("**Backend endpoint:**", BACKEND_SEND_URL)
