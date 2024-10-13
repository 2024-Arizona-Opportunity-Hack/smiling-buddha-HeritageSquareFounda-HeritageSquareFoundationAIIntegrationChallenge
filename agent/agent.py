# from langchain.vectorstores import Qdrant
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langgraph.prebuilt import create_react_agent

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

openai_llm = OpenAI(
    temperature=0.7, 
    model="gpt-3.5-turbo", 
    openai_api_key=os.getenv('OPENAI_API_KEY')
)
embedding_model = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY')
)
print(embedding_model)
qdrant_client = QdrantClient(url = os.getenv('QDRANT_ENDPOINT'), api_key = os.getenv('QDRANT_API_KEY'))
qdrant_vector_store = QdrantVectorStore(client = qdrant_client, collection_name = "Heritage_Square",embedding = embedding_model)


retriever = qdrant_vector_store.as_retriever()


### Build retriever tool ###
tool = create_retriever_tool(
    retriever,
    "blog_post_retriever",
    "Searches and returns excerpts from the Autonomous Agents blog post.",
)
tools = [tool]


graph = create_react_agent(llm, tools)

inputs = {"messages": [("user", "What type of documents you have?")]}
for s in graph.stream(inputs, stream_mode="values"):
    message = s["messages"][-1]
    if isinstance(message, tuple):
        print(message)
    else:
        message.pretty_print()

