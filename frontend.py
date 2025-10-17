import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000" 
st.set_page_config(page_title="Knowledge-base Search Engine", page_icon="📘", layout="wide")
st.title("Knowledge-base Search Engine")
st.write("Chat with your documets!")

st.sidebar.header("Settings")
session_id = st.sidebar.text_input("Session ID:", value="default_session")
text_input_data = ""
uploaded_files = None

st.sidebar.subheader("Input Type")
mode = st.sidebar.radio("Choose input:", ["📄 PDF", "📝 Text", "Both"])
uploaded_files = []
text_input_data = ""
if mode in ["📄 PDF", "Both"]:
    uploaded_files = st.sidebar.file_uploader(
        "Upload your PDFs", type="pdf", accept_multiple_files=True
    )

if mode in ["📝 Text", "Both"]:
    text_input_data = st.sidebar.text_area("Paste your text here:")

if st.sidebar.button("📤 Process Input"):
    data = {"session_id": session_id, "text_input": text_input_data}
    files = [("files", (f.name, f.read(), "application/pdf")) for f in uploaded_files] if uploaded_files else None

    res = requests.post(f"{BACKEND_URL}/upload", data=data, files=files)
    if res.ok:
        st.session_state.docs_available = True
        st.success("✅ Input processed successfully!")
    else:
        st.error("Failed to process input. Try again.")


if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if st.sidebar.button("🗑️ Clear Chat History"):
    response = requests.post(f"{BACKEND_URL}/clear", data={"session_id": session_id})
    if response.ok:
        st.session_state.chat_history = []
        st.success("Chat history cleared!")

st.subheader("Ask your question")

def submit_question():
    user_input = st.session_state.chat_input.strip()
    if not user_input:
        return

    st.session_state.chat_history.append({"type": "human", "content": user_input})

    response = requests.post(f"{BACKEND_URL}/ask", data={"session_id": session_id, "question": user_input})
    if response.ok:
        answer = response.json().get("answer", "")
        st.session_state.chat_history.append({"type": "ai", "content": answer})

    st.session_state.chat_input = ""

st.text_input(
    "Type your question here...",
    key="chat_input",
    on_change=submit_question,
    placeholder="Enter your question and press Enter..."
)

chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        if msg["type"] == "human":
            st.markdown(f"""
            <div style='display:flex; justify-content:flex-end; margin-bottom:10px;'>
                <div style='background-color:#4CAF50; color:white; padding:10px 15px; border-radius:15px 15px 0 15px; max-width:70%; word-wrap:break-word;'>
                    <b>You:</b><br>{msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif msg["type"] == "ai":
            st.markdown(f"""
            <div style='display:flex; justify-content:flex-start; margin-bottom:10px;'>
                <div style='background-color:#f1f0f0; color:black; padding:10px 15px; border-radius:15px 15px 15px 0; max-width:70%; word-wrap:break-word;'>
                    <b>Assistant:</b><br>{msg['content']}
                </div>  
            </div>
            """, unsafe_allow_html=True)
