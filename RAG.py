# Model 
from langchain.chat_models import init_chat_model
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
# Load & Chunk
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, Docx2txtLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# FAISS Vector Store
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from uuid import uuid4
from langchain_core.documents import Document
# Neo4j Database
from langchain_experimental.graph_transformers import LLMGraphTransformer
from prompt import PROMPTS
from langchain_core.prompts import SystemMessagePromptTemplate, PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_neo4j import Neo4jGraph, Neo4jVector
from langchain.chains import RetrievalQA
from pydantic import BaseModel, Field
from typing_extensions import List
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
import re
from openai_interacter import OpenAIChatInterface

# Initialize embeddings model
#embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

MERGE_NODES_QUERY = """
MATCH (nodeToKeep), (nodeToRemove)
WHERE id(nodeToKeep) = $idToKeep AND id(nodeToRemove) = $idToRemove
CALL apoc.refactor.mergeNodes([nodeToKeep, nodeToRemove], {properties:'overwrite'}) YIELD node
RETURN id(node) as mergedNodeId
"""

# Load and Segmentation
def load_and_chunk_documents(directory):
    loaders = [
        DirectoryLoader(directory, glob="**/*.pdf", loader_cls=PyPDFLoader),
        DirectoryLoader(directory, glob="**/*.docx", loader_cls=Docx2txtLoader),
        DirectoryLoader(directory, glob="**/*.txt", loader_cls=TextLoader),
        DirectoryLoader(directory, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader),
    ]
    docs = []
    for loader in loaders:
        docs.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=2025, chunk_overlap=185
    )
    chunks = text_splitter.split_documents(docs)
    return chunks

# Create FAISS Vector Store
def create_vector_store(documents, persist_directory):
    index = faiss.IndexFlatL2(len(embedding.embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=embedding,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)
    vector_store.save_local(persist_directory)
    return vector_store

# Neo4j Knowledge Graph
def create_knowledge_graph(documents, neo4j_url, neo4j_user, neo4j_password):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.28)
    
    PROMPT = PROMPTS["VERSATILE"]
    FINAL_TIP = HumanMessagePromptTemplate(
        prompt=PromptTemplate.from_template("""Tip: Make sure to answer in the correct format and do not include any explanations. Use the given format to extract information from the following input: {input}""")
    )
    extract_prompt = ChatPromptTemplate.from_messages([PROMPT, FINAL_TIP])

    # allowed_nodes = ["Giảng viên", "Học phần", "Ngành học", "Sinh viên", "Tài liệu", "Tài liệu online", "Tình trạng học tập" "Lớp", "Đơn vị", "Học phí"]
    # allowed_relationships = ["GIẢNG_DẠY", "THEO_CHUYÊN_NGÀNH", "CÓ_TÌNH_TRẠNG", "THUỘC_LỚP", "THEO_HỌC", "LÀ_TÀI_LIỆU_CHO", "LÀ_TÀI_LIỆU_TRỰC_TUYẾN_CHO" "CẦN_NỘP", "LÀM_VIỆC_TẠI"]
    # node_properties=['studentId', 'name', 'dob', 'status', 'amount', 'vietnameseName', 'englishName', 'name', 'title', 'authors', 'publisherInfo', 'link', 'type']
    
    llm_transformer = LLMGraphTransformer(llm=llm, prompt=extract_prompt,
        # allowed_nodes=allowed_nodes,
        # allowed_relationships=allowed_relationships,
        # node_properties=node_properties,
    )
    
    graph_documents = llm_transformer.convert_to_graph_documents(documents)
    graph = Neo4jGraph(url=neo4j_url, username=neo4j_user, password=neo4j_password, refresh_schema=False)
    graph.add_graph_documents(
        graph_documents,
        baseEntityLabel=True,
        include_source=True,
    )
    # graph.query(
    # "CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]")
    return graph



# Neo4j Vector Index
def create_vector_index(neo4j_url, neo4j_user, neo4j_password):
    # Initialize Vector Storage
    vector_index = Neo4jVector.from_existing_graph(
        embedding=embedding,
        url=neo4j_url,
        username=neo4j_user,
        password=neo4j_password,
        node_label="Document",
        text_node_properties=["text"],
        embedding_node_property='embedding',
        search_type="hybrid"
    )
    return vector_index

# Unstructured retrieval from FAISS Vector Store
def unstructured_retriever(query: str, vector_store) -> str:
    threshold = 0.61
    
    results_with_scores = vector_store.similarity_search_with_score(
        query=query,
        k=vector_store.index.ntotal,
    )
    
    chunks_below_threshold = []
    final_chunks = []
    
    for doc, score in results_with_scores:
        if score < threshold:
            chunks_below_threshold.append((doc, score))

    if chunks_below_threshold:
        if len(chunks_below_threshold) > 4:
            # Lấy 4 đoạn có số điểm thấp nhất
            chunks_below_threshold.sort(key=lambda item: item[1])  # Sắp xếp theo điểm số tăng dần
            
            final_chunks = [doc for doc, score in chunks_below_threshold[:4]]
        else:
            # Lấy tất cả các đoạn có điểm dưới 0.85
            final_chunks = [doc for doc, score in chunks_below_threshold]
    else:
        # Không có đoạn nào dưới 0.85, lấy 5 đoạn có số điểm thấp nhất
        results_with_scores.sort(key=lambda item: item[1])  # Sắp xếp theo điểm số tăng dần
        final_chunks = [doc for doc, score in results_with_scores[:5]]

    result = ""
    for i, chunk in enumerate(final_chunks):
        result += f"Context {i+1}: {chunk.page_content}\n"
    
    return result 

# Structured retriever from Neo4j Knowledge Graph
def structured_retriever(query: str, graph) -> str:

    """
    Collects the neighborhood of entities mentioned
    in the question
    """
    # print("\n[Structured Retriever] Processing question:", question)
    
    result = ""
    # Extract entities from question
    # print("\n[Structured Retriever] Extracting entities...")
    entities = extract_entities(text=query)
    # print("[Structured Retriever] Found entities:", entities)
    
    # Process each entity
    for entity in entities.names:
        
        # Generate full text query
        query = generate_full_text_query(entity)
        
        # Execute graph query to get the neightborhood of entities in user query
        # print("[Structured Retriever] Executing graph query...")
        response = graph.query(
            """CALL db.index.fulltext.queryNodes('entity', $query, {limit:2})
            YIELD node,score
            CALL {
              MATCH (node)-[r:!MENTIONS]->(neighbor)
              RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
              UNION
              MATCH (node)<-[r:!MENTIONS]-(neighbor)
              RETURN neighbor.id + ' - ' + type(r) + ' -> ' +  node.id AS output
            }
            RETURN output LIMIT 50
            """,
            {"query": query},
        )
        
        # Process results
        relationships = [el['output'] for el in response]
        # print(f"[Structured Retriever] Found {len(relationships)} relationships")
        if len(relationships) == 0:
            print(f"[Structured Retriever] Warning: No relationships found for entity '{entity}'")
            
        result += "\n".join([el['output'] for el in response])
    
    # print("\n[Structured Retriever] Retrieval complete")
    return result

# Function to process text and extract entities
def extract_entities(text):
    # Define the messages to send to the model 
    messages = [
        {
            "role": "system",
            "content": "You are extracting organization, place, event and person entities from the text."
        },
        {
            "role": "user",
            "content": "Extract the entities from the following text: {question}"
        }
    ]
    
    formatted_messages = [
        {"role": "system", "content": messages[0]["content"]},
        {"role": "user", "content": messages[1]["content"].replace("{question}", text)}
    ]

    # Create a new GPT-4o model instance
    entity_llm = OpenAIChatInterface(model_name="gpt-4o-mini", temperature=0.85, initial_messages=formatted_messages)
    entity_llm.enable_structured_output(Entities)
    return entity_llm.parse_structured_output()

# Handling characters in the user query
def remove_lucene_chars(text: str) -> str:
    return re.sub(r'[+\-&|!(){}[\]^"~*?:\\]', ' ', text)

# Generate full text query for Neo4j
def generate_full_text_query(input: str) -> str:
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    for word in words[:-1]:
        full_text_query += f" {word}~2 AND"
    full_text_query += f" {words[-1]}~2"
    return full_text_query.strip()

# Hybrid Search: Combine structured and unstructured retrieval
def hybrid_retriever(query: str, vector_store, graph) -> str:
    """
    Hybrid retriever that combines unstructured and structured retrieval
    """
    # print("\n[Hybrid Retriever] Processing question:", question)
    
    unstructured_data = unstructured_retriever(query, vector_store)
    structured_data = structured_retriever(query, graph)
    
    # Combine results
    result = f"Unstructured Data:\n{unstructured_data}\n\nStructured Retrieval:\n{structured_data}"
    
    return result

# Define the entities type 
class Entities(BaseModel):
    names: List[str] = Field(
        ...,
        description="All the person, place, organization, time, title or event entities that "
        "appear in the text",
    )

def get_llm(model_option, temperature):
    if model_option == "DeepSeek-R1":
        llm = ChatGroq(model="deepseek-r1-distill-llama-70b", temperature=temperature)
    elif model_option == "GPT-4o-mini":
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
    elif model_option == "Llama3.3":
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=temperature)
    elif model_option == "Ollama":
        llm = ChatOllama(
            model="llama3.1:8b-instruct-q8_0",
            temperature=temperature,
            num_predict=256,
        )
    else:
        llm = None
    return llm