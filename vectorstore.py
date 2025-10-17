import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import Document
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(model="gpt-4o")

def create_rag_from_content(pdf_paths: list = None, text_content: str = None):
    documents = []
    if pdf_paths:
        for pdf in pdf_paths:
            loader = PyPDFLoader(pdf)
            documents.extend(loader.load())

    if text_content and text_content.strip():
        documents.append(Document(page_content=text_content.strip(), metadata={"source": "user_text"}))

    if not documents:
        raise ValueError("No PDFs or text provided to create RAG.")

    #split into chunks 
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    splits = splitter.split_documents(documents)

    #create vectorstore and retriever 
    vectorstore = Chroma.from_documents(splits, embeddings)
    retriever = vectorstore.as_retriever()

    context_q_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given the chat history and the latest user question, "
                   "formulate a standalone question. Do NOT answer."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, context_q_prompt)

    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following retrieved context to answer. "
        "If you don't know reply Can not answer form the provided documents. Keep answers concise (max 3 sentences).\n\n{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    #chaining
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain
