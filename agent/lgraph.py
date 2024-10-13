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




import os
from dotenv import load_dotenv
load_dotenv()
memory = MemorySaver()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=os.getenv('OPENAI_API_KEY'))


embedding_model = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY')
)
# print(embedding_model)
qdrant_client = QdrantClient(url = os.getenv('QDRANT_ENDPOINT'), api_key = os.getenv('QDRANT_API_KEY'))
qdrant_vector_store = QdrantVectorStore(client = qdrant_client, collection_name = "Heritage_Square",embedding = embedding_model)

# vectorstore = InMemoryVectorStore.from_documents(
#     documents=splits, embedding=OpenAIEmbeddings()
# )
retriever = qdrant_vector_store.as_retriever()


### Build retriever tool ###
tool = create_retriever_tool(
    retriever,
    "blog_post_retriever",
    "Searches and returns excerpts from the Autonomous Agents blog post.",
)
tools = [tool]


graph = create_react_agent(llm, tools, checkpointer=memory)
config = {"configurable": {"thread_id": "abc123"}} 

inputs = {"messages": [("user", "What type of documents you have?")]}
for s in graph.stream(inputs, stream_mode="values"):
    message = s["messages"][-1]
    if isinstance(message, tuple):
        print(message)
    else:
        message.pretty_print()