import asyncio
import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from IPython.display import display, Image
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode, tools_condition
from embed_n_retrieve import retrieve_relevant_documents

# Load environment variables 
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize memory for context retention
memory = MemorySaver()

# Initialize Agent workflow state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    
graph_builder = StateGraph(State)

# Initializing llm models
rag_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

# Including tools
online_search_tool = TavilySearchResults(max_results=2)
tools = [online_search_tool]
llm_with_tools = rag_llm.bind_tools(tools)

# Defining nodes
async def chatbot(state: State):
    user_query = state["messages"][-1].content
    relevant_docs = await retrieve_relevant_documents(user_query)
    context = "\n\n".join(relevant_docs)

    augmented_query = f"""
    You are an Engineering Support AI Chatbot, a specialized assistant designed to provide 
    real-time technical support to field engineers. 
    Your primary function is to deliver accurate, concise, and actionable answers based on 
    the organization's internal documentation, manuals, schematics, and troubleshooting 
    guides. We have provided you with context from the organization's internal documentation, manuals, schematics, and troubleshooting 
    guides information below regarding the user's query.
    ---------------------
    Context: {context}
    ---------------------
    Given this information, please answer the question. User Query: {user_query}"""

    #Create a new message with the augmented query.
    augmented_message = [{"role": "user", "content": augmented_query}]

    #Append to the existing message history.
    new_messages = state["messages"] + augmented_message

    return {"messages": [rag_llm.invoke(new_messages)]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# Setting entry, continue edges & exit point
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")

# Compiling the graph using checkpointer to include memory to it
graph = graph_builder.compile(checkpointer=memory)

# try:
#     graph_image = graph.get_graph().draw_mermaid_png()
#     display(Image(graph_image))
# except Exception as e:
#     print(f"Failed to display graph: {e}")
#     print(graph.get_graph().print_ascii())

config = {"configurable": {"thread_id":"user_1"}}
async def run_agent(input_message):
    full_response = []
    async for output in graph.astream({"messages": [{"role": "user", "content": input_message}]}, config=config):
        if "chatbot" in output:
            ai_message = output["chatbot"]["messages"][0]
            # print(ai_message.content)
            return ai_message.content

if __name__ == "__main__":
    user_input = "Tell me what was said about 'Removing Unused Programs'."
    response = asyncio.run(run_agent(user_input))
    print("\nUser Question:", user_input)
    print("\nResponse:", response)
    
