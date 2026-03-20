import streamlit as st
import requests
import time
import random

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Virtus AI", layout="wide")

# -------------------------
# AVATARS
# -------------------------

VIRTUS_AVATAR = "C:\\Users\\rishikesh.n\\Documents\\Virtus\\frontend\\Assets\\Virtus.png"
USER_AVATAR = "C:\\Users\\rishikesh.n\\Documents\\Virtus\\frontend\\Assets\\User.png"

# -------------------------
# STYLING
# -------------------------

st.markdown("""
<style>

[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 14px;
}

[data-testid="stChatMessage"]:has([aria-label="assistant"]) {
    background-color: #f6f3ea;
}

[data-testid="stChatMessage"]:has([aria-label="user"]) {
    background-color: #dbeafe;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stStatusWidget"] {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

st.title("Virtus")
st.caption("A Stoic AI guide")

# -------------------------
# SESSION STATE
# -------------------------

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("Conversations")
st.sidebar.info("📚 Upload knowledge from the 'Knowledge Upload' page")
# Create new chat
if st.sidebar.button("New Chat"):

    res = requests.post(
        f"{API_URL}/virtus/conversations",
        json={"user_id": 1}
    )

    if res.status_code == 200:
        data = res.json()

        if "conversation_id" in data:
            st.session_state.conversation_id = data["conversation_id"]

        if "conversation_id" in data:
            st.session_state.conversation_id = data["conversation_id"]
            st.session_state.messages = []
            st.rerun()

    else:
        st.error("Failed to create conversation")

# Load conversation list
# Load conversations
res = requests.get(f"{API_URL}/virtus/users/1/conversations")
print(res.json())
if res.status_code == 200:
    conversations = res.json()
else:
    conversations = []

# Display conversations
for conv in conversations:

    col1, col2 = st.sidebar.columns([4,1])

    label = (
        f"🟢 Chat {conv['id']}"
        if conv["id"] == st.session_state.conversation_id
        else f"Chat {conv['id']}"
    )
# -------------------------
# LOAD CHAT HISTORY
# -------------------------
    with col1:
        if st.button(label, key=f"chat_{conv['id']}"):

            # switch conversation
            st.session_state.conversation_id = conv["id"]

            # fetch messages for that chat
            res = requests.get(
                f"{API_URL}/virtus/conversations/{conv['id']}"
            )

            if res.status_code == 200:
                st.session_state.messages = res.json()["messages"]
            else:
                st.session_state.messages = []

            st.rerun()

    with col2:
        if st.button("❌", key=f"delete_{conv['id']}"):

            res = requests.delete(
                f"{API_URL}/virtus/conversations/{conv['id']}"
            )

            if res.status_code == 200:

                if st.session_state.conversation_id == conv["id"]:
                    st.session_state.conversation_id = None
                    st.session_state.messages = []

                st.rerun()

# -------------------------
# DISPLAY MESSAGES
# -------------------------

for msg in st.session_state.messages:

    avatar = USER_AVATAR if msg["role"] == "user" else VIRTUS_AVATAR

    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])
# -------------------------
# CHAT INPUT
# -------------------------

prompt = st.chat_input("Talk to Virtus")

if prompt:

    # show user message immediately
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(prompt)

    # create conversation if none exists
    if st.session_state.conversation_id is None:

        res = requests.post(
            f"{API_URL}/virtus/conversations",
            json={"user_id": 1}
        )

        if res.status_code == 200:

            data = res.json()
            print(data)

        if "conversation_id" in data:
            st.session_state.conversation_id = data["conversation_id"]
            st.session_state.messages = []
            st.rerun()
        else:
            st.error(data)

    # thinking animation
    with st.chat_message("assistant", avatar=VIRTUS_AVATAR):

        placeholder = st.empty()

        thinking = [
            "⚖️ Virtus weighs your question",
            "📜 Virtus consults the scrolls",
            "🧠 Virtus reflects deeply"
        ]

        for i in range(3):
            placeholder.markdown(thinking[i % len(thinking)] + "." * (i+1))
            time.sleep(0.4)

        # ask backend
        res = requests.post(
            f"{API_URL}/virtus/conversations/{st.session_state.conversation_id}/message",
            json={"question": prompt}
        )

        if res.status_code == 200:

            answer = res.json()["response"]

            placeholder.markdown(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })
            answer = res.json()["response"]

            # DEBUG
            if "context_used" in res.json():
                st.caption("Context used:")
                st.write(res.json()["context_used"])

        else:
            placeholder.markdown("Virtus could not respond.")

    st.rerun()