from langchain.vectorstores import Qdrant
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# openAI_key = userdata.get(OPEN_AI)
# Initialize OpenAI GPT-4 with the desired temperature and API key
openai_llm = OpenAI(
    temperature=0.7, 
    model="gpt-3.5-turbo", 
    openai_api_key=userdata.get("OPEN_AI")
)
embedding_model = OpenAIEmbeddings(
    openai_api_key=userdata.get("OPEN_AI")
)
print(embedding_model)
qdrant_client = QdrantClient(url = userdata.get("QDRANT_ENDPOINT"), api_key = userdata.get("QDRANT_API_KEY"))
doc_store = QdrantVectorStore(client = qdrant_client, collection_name = "Heritage_Square",embedding = embedding_model)

