from fastapi import FastAPI, UploadFile, Form,File
from typing import List,Optional
import shutil
import os
from session_history import SessionManager
from vectorstore import create_rag_from_content
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv()
app = FastAPI(title="RAG Knowledge Base")

session_manager = SessionManager()
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

llm = ChatOpenAI(model="gpt-4o")
rag_chains = {}

@app.post("/upload")
async def upload_content(
    session_id: str = Form(...),
    text_input: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    pdf_paths = []

    if files:
        for file in files:
            path = os.path.join(UPLOAD_DIR, file.filename)
            with open(path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            pdf_paths.append(path)

    retriever = create_rag_from_content(pdf_paths=pdf_paths, text_content=text_input)
    rag_chains[session_id] = retriever

    uploaded_count = len(pdf_paths)
    text_msg = " + text input" if text_input else ""
    return {
        "status": "success",
        "message": f"{uploaded_count} PDFs uploaded{text_msg}"
    }

@app.post("/ask")
async def ask_question(session_id: str = Form(...), question: str = Form(...)):
    if session_id not in rag_chains:
        return {"status": "error", "message": "Upload PDFs first"}

    rag_chain = rag_chains[session_id]
    history = session_manager.get_session_history(session_id)

    from langchain_core.runnables.history import RunnableWithMessageHistory
    conversational_chain = RunnableWithMessageHistory(
        rag_chain,
        session_manager.get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )
    conversational_chain.invoke({"input": question}, config={"configurable": {"session_id": session_id}})
    # Return the latest AI response
    ai_message = history.messages[-1].content if history.messages else ""
    return {"answer": ai_message}

@app.post("/clear")
async def clear_history(session_id: str = Form(...)):
    session_manager.clear_session(session_id)
    return {"status": "success", "message": "Chat history cleared"}



