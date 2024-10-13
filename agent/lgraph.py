# import bs4
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from langchain_core.prompts import PromptTemplate



import os
from dotenv import load_dotenv
load_dotenv()
memory = MemorySaver()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=os.getenv('OPENAI_API_KEY'))


embedding_model = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY')
)
# print(embedding_model)
qdrant_client = QdrantClient(url = os.getenv('QDRANT_ENDPOINT'), api_key = os.getenv('QDRANT_API_KEY'))
qdrant_vector_store = QdrantVectorStore(
    client = qdrant_client, 
    collection_name = "Heritage_Square",
    embedding = embedding_model,
    content_payload_key  = "_node_content",
    metadata_payload_key = "custom_metadata"
    )

retriever = qdrant_vector_store.as_retriever()

# documents = qdrant_vector_store.similarity_search("What are the benifits of sponsering Gin & Jazz is the annual fundraising gala", k=2)

# print(documents[0].page_content,"metadata" ,documents[0].metadata)
## Build retriever tool ###
tool = create_retriever_tool(
    retriever,
    "Qdrant_Vector_Search_Retriever",
    "Search Documents for the relevant information",
)
tools = [tool]

system_message = "You are virual Asistant for Heritage Sqlare Organization. always include dDRive_DocName : dDRive_DocLink in markdown format at the end for all the dDRive_DocNames and dDRive_DocLinks" 
agent_executor = create_react_agent(llm, tools,state_modifier=system_message,  checkpointer=memory)
config = {"configurable": {"thread_id": "abc123"}} 

# inputs = {"messages": [("user", "What type of documents you have?")]}
query = "What are the benifits of sponsering Gin & Jazz is the annual fundraising gala"

events = agent_executor.stream(
    {"messages": [HumanMessage(content=query)]},config,
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()