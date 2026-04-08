import streamlit as st
import requests
import zlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from deep_translator import GoogleTranslator

BACKEND_GET_URL = "https://<YOUR-BACKEND-URL>/get"

st.set_page_config(page_title="CrypTalk Receiver", page_icon="📥", layout="centered")
st.title("📥 CrypTalk Receiver")
st.caption("Fetch and decrypt the latest secure message")

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


def decrypt(encrypted_hex, key_hex, nonce_hex):
    aes = AESGCM(bytes.fromhex(key_hex))
    return aes.decrypt(bytes.fromhex(nonce_hex), bytes.fromhex(encrypted_hex), None)


def decompress(data):
    return zlib.decompress(data).decode()


if st.button("🔄 Fetch Latest Message"):
    with st.spinner("Fetching secure message..."):
        try:
            response = requests.get(BACKEND_GET_URL, timeout=15)
        except requests.RequestException as error:
            st.error(f"Request failed: {error}")
            st.stop()

        if response.status_code != 200:
            st.error("No secure message available yet.")
            st.stop()

        data = response.json()
        if not data:
            st.warning("No message stored in the backend.")
            st.stop()

        try:
            decrypted = decrypt(data["encrypted"], data["key"], data["nonce"])
            decrypted_text = decompress(decrypted)
        except Exception as error:
            st.error(f"Decryption failed: {error}")
            st.stop()

        receiver_lang = data.get("receiver_lang", "English")
        final_message = decrypted_text

        if receiver_lang != "English":
            try:
                final_message = GoogleTranslator(source="en", target=LANG_CODES[receiver_lang]).translate(decrypted_text)
            except Exception:
                final_message = decrypted_text

        st.success("✅ Secure message received")
        st.markdown("---")
        st.write("**Sender:**", data.get("sender", "Unknown"))
        st.write("**Receiver:**", data.get("receiver", "Unknown"))
        st.write("**Emotion tag:**", data.get("emotion", "N/A"))
        st.write("**Translated to:**", receiver_lang)
        st.markdown("### 📩 Message")
        st.code(final_message)
