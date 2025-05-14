import streamlit as st
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Chat Model & Embedding
from langchain.chat_models import init_chat_model
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_neo4j import Neo4jGraph, Neo4jVector

# Prompt template
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate
from prompt import PROMPTS
import RAG

# Load environment variables
load_dotenv(find_dotenv())
os.environ["GROQ_API_KEY"] = str(os.getenv("GROQ_API_KEY"))
os.environ["OPENAI_API_KEY"] = str(os.getenv("OPENAI_API_KEY"))

NEO4J_URI = str(os.getenv("NEO4J_URI"))
NEO4J_USERNAME = str(os.getenv("NEO4J_USERNAME"))
NEO4J_PASSWORD = str(os.getenv("NEO4J_PASSWORD"))

# Constants
KNOWLEDGE_DIR = "KnowledgeBase"
VECTOR_STORAGE_PATH = "VectorStorage"

# Cache vector store creation
@st.cache_resource
def load_or_create_vector_store(_documents, path):
    start_time = time.time()
    vector_store = RAG.create_vector_store(_documents, path)
    st.write(f"Thời gian tạo Vector Store: {time.time() - start_time:.2f} giây")
    return vector_store

# Cache knowledge graph creation
@st.cache_resource
def load_or_create_knowledge_graph(_documents, uri, username, password):
    start_time = time.time()
    graph = RAG.create_knowledge_graph(_documents, uri, username, password)
    st.write(f"Thời gian tạo Knowledge Graph: {time.time() - start_time:.2f} giây")
    return graph

def streamlit_ui():
    # --- Cấu hình trang ---
    st.set_page_config(
        page_title="uMentor",
        page_icon=":robot_face:",
    )

    # --- Thanh bên ---
    with st.sidebar:
        st.title("Tùy chọn")
        model_option = st.selectbox(
            "Danh sách mô hình:", ["DeepSeek-R1", "GPT-4o-mini", "Llama3.3", "Local"]
        )
        temperature = st.slider("Temperature:", 0.0, 1.0, 0.28)
        st.markdown("---")
        st.header("Tải tài liệu")
        uploaded_files = st.file_uploader("Chọn file để tải lên", accept_multiple_files=True)
        process_button_pressed = False

        if uploaded_files:
            if not os.path.exists(KNOWLEDGE_DIR):
                os.makedirs(KNOWLEDGE_DIR)
            for uploaded_file in uploaded_files:
                file_path = os.path.join(KNOWLEDGE_DIR, uploaded_file.name)
                try:
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    # st.success(f"Đã tải lên và lưu file: {uploaded_file.name} vào thư mục '{KNOWLEDGE_DIR}'")    
                except Exception as e:
                    st.error(f"Lỗi khi lưu file {uploaded_file.name}: {e}")
            process_button_pressed = st.button("Xử lý tài liệu cho RAG")
        else:
            st.markdown("Bạn có thể tải tài liệu lên để cập nhật kiến thức cho chatbot.")

        # Khởi tạo session state
        if "vector_store" not in st.session_state:
            st.session_state["vector_store"] = None
        if "knowledge_graph" not in st.session_state:
            st.session_state["knowledge_graph"] = None

        # Load lại vector store cũ nếu không có file mới
        if not uploaded_files and os.path.exists(os.path.join(VECTOR_STORAGE_PATH, "index.faiss")):
            if st.session_state["vector_store"] is None:
                with st.spinner("Đang tải vector store đã lưu..."):
                    try:
                        st.session_state["vector_store"] = FAISS.load_local(
                            VECTOR_STORAGE_PATH,
                            RAG.embedding,
                            allow_dangerous_deserialization=True
                        )
                        st.success("Đã tải vector store.")
                    except Exception as e:
                        st.error(f"Lỗi khi tải vector store: {e}")

            if st.session_state["knowledge_graph"] is None and NEO4J_URI and NEO4J_USERNAME and NEO4J_PASSWORD:
                with st.spinner("Đang kết nối đến Knowledge Graph..."):
                    try:
                        st.session_state["knowledge_graph"] = Neo4jGraph(
                            url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD
                        )
                        st.success("Đã kết nối đến Knowledge Graph.")
                    except Exception as e:
                        st.error(f"Lỗi khi kết nối đến Knowledge Graph: {e}")

        # Xử lý tài liệu khi nhấn nút
        elif process_button_pressed and uploaded_files:
            with st.spinner("Đang xử lý tài liệu..."):
                start_time = time.time()
                documents = RAG.load_and_chunk_documents(KNOWLEDGE_DIR)
                st.write(f"Thời gian Tải và Chunk: {time.time() - start_time:.2f} giây")

                if documents:
                    st.session_state["vector_store"] = load_or_create_vector_store(documents, VECTOR_STORAGE_PATH)
                    st.success("Đã tạo Vector Store.")
                else:
                    st.warning("Không có tài liệu nào được xử lý.")
                    st.session_state["vector_store"] = None

                if documents and NEO4J_URI and NEO4J_USERNAME and NEO4J_PASSWORD:
                    try:
                        st.session_state["knowledge_graph"] = load_or_create_knowledge_graph(
                            documents, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
                        )
                        st.success("Đã tạo Knowledge Graph.")
                    except Exception as e:
                        st.error(f"Lỗi khi tạo Knowledge Graph: {e}")
                        st.session_state["knowledge_graph"] = None
                else:
                    st.warning("Không thể tạo Knowledge Graph. Kiểm tra cấu hình Neo4j.")

        st.markdown("---")
        st.markdown("uMentor 2025")

    # --- Phần hỏi đáp chatbot ---
    st.title("UET Mentor")
    st.markdown("Chào bạn! Tôi là chatbot hỗ trợ học tập của bạn. Hãy bắt đầu trò chuyện nhé!")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Nhập câu hỏi..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            vector_store = st.session_state.get("vector_store")
            graph = st.session_state.get("knowledge_graph")
            model = RAG.get_llm(model_option, temperature)

            if vector_store and graph and model:
                graph.query("CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]")
                context = RAG.unstructured_retriever(prompt, vector_store)
                ontology = RAG.structured_retriever(prompt, graph)

                system_template = PROMPTS["system_mission"]
                human_template = prompt + PROMPTS["human_message"]
                prompt_template = ChatPromptTemplate.from_messages(
                    [("system", system_template), ("user", human_template)]
                )
                final_prompt = prompt_template.invoke({"unstructured_data": context, "structured_data": ontology})

                try:
                    response = model.invoke(final_prompt)
                    answer = response.content
                    st.markdown(answer)
                    st.session_state["messages"].append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Lỗi khi tạo phản hồi: {e}")
            else:
                response = "Vui lòng kiểm tra: "
                if not model:
                    response += "Chưa chọn mô hình."
                elif vector_store is None:
                    response += "Vector Store chưa sẵn sàng."
                elif graph is None:
                    response += "Knowledge Graph chưa sẵn sàng."
                st.markdown(response)

if __name__ == "__main__":
    streamlit_ui()