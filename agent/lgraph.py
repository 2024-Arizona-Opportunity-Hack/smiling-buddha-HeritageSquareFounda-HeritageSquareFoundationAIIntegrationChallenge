# import bs4
import asyncio
import os

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage)
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=os.getenv('OPENAI_API_KEY'))


embedding_model = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY')
)
qdrant_client = QdrantClient(url = os.getenv('QDRANT_ENDPOINT'), api_key = os.getenv('QDRANT_API_KEY'))
qdrant_vector_store = QdrantVectorStore(
    client = qdrant_client, 
    collection_name = "Heritage_Square",
    embedding = embedding_model,
    content_payload_key  = "_node_content",
    metadata_payload_key = "custom_metadata"
    )

retriever = qdrant_vector_store.as_retriever()
## Build retriever tool ###
tool = create_retriever_tool(
    retriever,
    "Qdrant_Vector_Search_Retriever",
    "Search Documents for the relevant information",
)


template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

You are virual Asistant for Heritage Square Organization. always include dDRive_DocName, dDRive_DocLink in markdown format  as [dDRive_DocNames] : [dDRive_DocLink] at the end if you have those values in last message.
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question


Begin!
Final answer should be in markdown format with proper bullet points and href link
Question: {input}
Thought:{agent_scratchpad}'''

prompt = PromptTemplate.from_template(template)


tools = [tool]

agent = create_react_agent(llm,tools,prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)


async def ask_chat(query, chatHistory=[]):
    # This returns a synchronous generator
    chathistory_new = [] # Map the ChatHistory to chatHistory
    for entry in chatHistory:
        role = entry["role"]
        content = entry["content"]

        if role == "user":
            chathistory_new.append(HumanMessage(content=content))
        elif role == "assistant":
            chathistory_new.append(AIMessage(content=content))
    return agent_executor.invoke({"input": query, "chat_history": chathistory_new})



# ask_chat("How are you?")