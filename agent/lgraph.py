# import bs4
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
from langgraph.checkpoint.memory import MemorySaver
# from langgraph.prebuilt import create_react_agent
from qdrant_client import QdrantClient

load_dotenv()

# prompt = hub.pull("hwchase17/react")
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


template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question
You are virual Asistant for Heritage Square Organization. always include dDRive_DocName : dDRive_DocLink in markdown format at the end for all the dDRive_DocNames and dDRive_DocLinks


Begin!

Question: {input}
Thought:{agent_scratchpad}'''

prompt = PromptTemplate.from_template(template)


tools = [tool]

# system_message = "You are virual Asistant for Heritage Sqlare Organization. always include dDRive_DocName : dDRive_DocLink in markdown format at the end for all the dDRive_DocNames and dDRive_DocLinks" 
# agent_executor = create_react_agent(llm, tools,state_modifier=system_message,  checkpointer=memory)

agent = create_react_agent(llm,tools,prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)



# config = {"configurable": {"thread_id": "abc123"}}

# inputs = {"messages": [("user", "What type of documents you have?")]}
# query = "What are the benifits of sponsering Gin & Jazz is the annual fundraising gala"

# events = agent_executor.stream(
#     {"messages": [HumanMessage(content=query)]},config,
#     stream_mode="values",
# )
chathistory = []
while True:
    user_input = input("User: ")
    result= agent_executor.invoke({"input":user_input,"chat_history":chathistory})
    chathistory.append(HumanMessage(content=user_input))
    chathistory.append(AIMessage(content = result['output']))
    print(result["output"])
# for event in events:
#     event["messages"][-1].pretty_print()