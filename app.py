import os
import streamlit as st
from groq import Groq

# ─── Helper: Stream parser ────────────────────────
def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# ─── Load secrets from Streamlit Cloud ────────────
secrets = st.secrets

if "GROQ_API_KEY" not in secrets:
    st.error("❌ GROQ_API_KEY is missing from Streamlit Cloud secrets!")
    st.stop()

os.environ["GROQ_API_KEY"] = secrets["GROQ_API_KEY"]

INITIAL_RESPONSE = secrets.get("INITIAL_RESPONSE", "Hello! I'm Haseeb, your AI assistant. How can I help you today?")
INITIAL_MSG = secrets.get("INITIAL_MSG", "I’m ready to help.")

CHAT_CONTEXT = (
    "your name is Haseeb, "
    "You are an expert professional assistant. "
    "Write in concise, polite, and authoritative language. "
    "Provide well‑structured, actionable, and accurate responses. "
    "Maintain a tone of respect and competence, using active voice and clear sentences. "
    "When appropriate, organize replies with headings or bullet points. "
    "In uncertain cases, acknowledge limits and suggest next steps."
)

client = Groq()

# ─── Streamlit UI setup ───────────────────────────
st.set_page_config(page_title="Haseeb chatbot", layout="centered")
st.title("Haseeb chatbot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": INITIAL_RESPONSE}
    ]

# Display the full conversation
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── Handle new user input ────────────────────────
user_prompt = st.chat_input("Your message:")

if user_prompt:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Prepare context
    messages = [
        {"role": "system", "content": CHAT_CONTEXT},
        {"role": "assistant", "content": INITIAL_MSG},
        *st.session_state.chat_history
    ]

    try:
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Change if needed
            messages=messages,
            temperature=0.3,
            max_tokens=500,
            top_p=0.9,
            stream=True
        )
        # Display assistant response
        with st.chat_message("assistant"):
            response = st.write_stream(parse_groq_stream(stream))
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"⚠️ Error from Groq API: {e}")

# ─── Clear Chat Button ────────────────────────────
if st.button("Clear Chat"):
    st.session_state.chat_history = [
        {"role": "assistant", "content": INITIAL_RESPONSE}
    ]
    st.rerun()
