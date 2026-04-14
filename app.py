import streamlit as st
import requests
import time

st.set_page_config(page_title="Therapist Chat", layout="centered")

# --------- CSS Styling ---------
st.markdown("""
<style>
/* Page background */
body {
    background-color: #0e1117;
}

/* Chat container */
.chat-container {
    max-width: 700px;
    margin: auto;
}

/* User bubble (right side) */
.user-bubble {
    background-color: #cce5ff;
    color: #000000;   /* ✅ black text */
    padding: 12px 16px;
    border-radius: 15px;
    margin: 8px 0;
    text-align: right;
    width: fit-content;
    margin-left: auto;
}

/* Bot bubble (left side) */
.bot-bubble {
    background-color: #f1f0f0;
    color: #000000;   /* ✅ black text */
    padding: 12px 16px;
    border-radius: 15px;
    margin: 8px 0;
    text-align: left;
    width: fit-content;
}

/* Input box */
.stChatInput > div {
    background-color: #1c1f26;
    border-radius: 20px;
}

</style>
""", unsafe_allow_html=True)

st.title("🧠 Therapist Chatbot")
st.caption("You're safe here. Talk freely.")

# --------- Session State ---------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------- Display Messages ---------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

# --------- Input ---------
user_input = st.chat_input("How are you feeling today?")

import uuid

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show user message immediately
    st.markdown(f'<div class="user-bubble">{user_input}</div>', unsafe_allow_html=True)

    # Call backend
    with st.spinner("Thinking..."):
        time.sleep(1)  # human feel
        try:
            response = requests.post(
                "http://localhost:8000/chat",
                json={"message": user_input, "session_id": st.session_state.session_id},
                timeout=60
            )
            bot_reply = response.json()["response"]

        except Exception as e:
            bot_reply = "⚠️ Backend is not running. Please start FastAPI server."

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        st.markdown(f'<div class="bot-bubble">{bot_reply}</div>', unsafe_allow_html=True)