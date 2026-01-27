import streamlit as st
from chatbot import get_answer_safe

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="RAG Website Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background-color: #f5f7fa;
}
.chat-box {
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.user {
    background-color: #dbeafe;
    text-align: right;
}
.bot {
    background-color: #ede9fe;
    text-align: left;
}
.header {
    text-align: center;
    font-size: 36px;
    font-weight: bold;
    color: #4f46e5;
}
.subheader {
    text-align: center;
    color: #475569;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<div class='header'>🤖 RAG-Powered Website Chatbot</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>Ask questions about ClaySys using AI</div><br>", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- CHAT DISPLAY ----------------
for role, message in st.session_state.chat_history:
    css = "user" if role == "You" else "bot"
    st.markdown(
        f"<div class='chat-box {css}'><b>{role}:</b> {message}</div>",
        unsafe_allow_html=True
    )

# ---------------- INPUT ----------------
query = st.chat_input("Ask a question about ClaySys...")

if query:
    st.session_state.chat_history.append(("You", query))

    with st.spinner("Thinking..."):
        answer = get_answer_safe(query)

    st.session_state.chat_history.append(("Bot", answer))
    st.rerun()
