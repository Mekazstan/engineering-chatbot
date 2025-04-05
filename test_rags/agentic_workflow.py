import os
from dotenv import load_dotenv
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from embed_n_retrieve import main_retriever
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize memory for context retention
memory = MemorySaver()

# Define the possible destinations
class RouteDecision(TypedDict):
    destination: Literal["retrieval", "naive", "tools"]

# Initialize Agent workflow state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    destination: RouteDecision
    answer: str

graph_builder = StateGraph(State)

# Initialize LLM models
rag_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

# Initialize tools
online_search_tool = TavilySearchResults(max_results=2)
tools = [online_search_tool]
llm_with_tools = rag_llm.bind_tools(tools)

# Define the decision maker
def decide_retrieval(state: State, config: RunnableConfig):
    user_query = state["messages"][-1].content
    decision_prompt = f"""
    Given the user query: "{user_query}", determine the next step.
    1. If the query requires information from the organization's documents, return "retrieval".
    2. If the query can be answered without external context, return "naive".
    3. If the query requires searching the internet, return "tools".
    Only respond with one of these three words: retrieval, naive, or tools. Don't add any other text to your response.
    Decision:
    """
    
    response = llm_with_tools.invoke(
        [HumanMessage(content=decision_prompt)],
        config=config
    )
    decision = response.content.strip().lower()
    print(f"Decision: {decision}")
    return {"destination": {"destination": decision}}

# Define the nodes
def retrieval_node(state: State, config: RunnableConfig):
    user_query = state["messages"][-1].content
    relevant_docs = main_retriever(user_query)
    context = "\n\n".join(relevant_docs)

    augmented_query = f"""
    You are an Engineering Support AI Chatbot, a specialized assistant designed to provide
    real-time technical support to field engineers.
    Your primary function is to deliver accurate, concise, and actionable answers based on
    the organization's internal documentation, manuals, schematics, and troubleshooting
    guides. We have provided you with context from the organization's internal documentation below:
    ---------------------
    Context: {context}
    ---------------------
    Question: {user_query}"""

    response = rag_llm.invoke(
        [HumanMessage(content=augmented_query)],
        config=config
    )
    return {"messages": [response], "answer": response.content}

def naive_node(state: State, config: RunnableConfig):
    user_query = None
    # Find the last human message (original query)
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_query = msg.content
            break
    
    if not user_query:
        return {"messages": [AIMessage(content="I couldn't find your original question.")]}
    
    # Check if we have search results in the state
    search_results = state.get("search_results")
    if search_results:
        context = search_results
        augmented_query = f"""
        Based on these search results:
        {context}
        
        Please answer this question: {user_query}
        """
    else:
        augmented_query = user_query

    response = rag_llm.invoke(
        [HumanMessage(content=augmented_query)],
        config=config
    )
    return {"messages": [response], "answer": response.content}

def generate_tool_calls(state: State, config: RunnableConfig):
    user_query = state["messages"][-1].content
    response = llm_with_tools.invoke(
        [HumanMessage(content=user_query)],
        config=config
    )
    return {"messages": [response]}

def tool_node(state: State):
    # Get the last AI message which should contain tool calls
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        raise ValueError("Last message must be an AIMessage with tool calls")
    
    # Call the tools and collect results
    tool_messages = []
    search_results = []
    for tool_call in last_message.tool_calls:
        if tool_call["name"] == "tavily_search_results_json":
            # Call the search tool
            result = online_search_tool.invoke(tool_call["args"])
            print(f"SEARCH RESULT: {result}\n")
            search_results.extend(result)
            # Create proper ToolMessage objects
            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                )
            )
    
    # Return both the tool messages and search results
    return {
        "messages": tool_messages,
        "search_results": search_results
    }

# Define the routing logic
def select_node(state: State) -> Literal["retrieval_node", "naive_node", "generate_tool_calls"]:
    dest = state["destination"]["destination"]
    if dest == "retrieval":
        return "retrieval_node"
    elif dest == "naive":
        return "naive_node"
    return "generate_tool_calls"

# Define where to go after tool execution
def route_after_tools(state: State) -> Literal["naive_node", END]:
    return "naive_node"

# Build the graph
graph_builder.add_node("decide_retrieval", decide_retrieval)
graph_builder.add_node("retrieval_node", retrieval_node)
graph_builder.add_node("naive_node", naive_node)
graph_builder.add_node("generate_tool_calls", generate_tool_calls)
graph_builder.add_node("tools", tool_node)

# Define the edges
graph_builder.add_edge(START, "decide_retrieval")
graph_builder.add_conditional_edges(
    "decide_retrieval",
    select_node
)
graph_builder.add_edge("generate_tool_calls", "tools")
graph_builder.add_conditional_edges(
    "tools",
    route_after_tools
)
graph_builder.add_edge("retrieval_node", END)
graph_builder.add_edge("naive_node", END)

# Compile the graph
graph = graph_builder.compile(checkpointer=memory)

# Simplified run function
# Run function
def run_agent(input_message):
    config = {"configurable": {"thread_id": "user_1"}}
    state = {"messages": [HumanMessage(content=input_message)]}
    while True:
        output = graph.invoke(state, config=config)
        # print("Output:", output)
        if "answer" in output:
            return output["answer"]
        elif "tool_code" in output:
            return f"Tool Result: {output['tool_code']}"
        elif isinstance(output, dict) and "messages" in output and isinstance(output["messages"][-1], AIMessage):
            return output["messages"][-1].content
        elif isinstance(output, dict) and "destination" in output and output["destination"]["destination"] == "tools":
            # LLM needs to decide which tool to use
            llm_response = llm_with_tools.invoke(state["messages"])
            state["messages"].append(llm_response)
        elif isinstance(output, dict) and "destination" in output:
            state["destination"] = output["destination"]
            # The next node will process based on the destination
        elif isinstance(output, dict) and "__end__" in output:
            return None  # Reached the end of the graph
        elif isinstance(output, dict) and "__exception__" in output:
            raise output["__exception__"] # Raise any exceptions

        # Update the state for the next step (if it's not an end state)
        if isinstance(output, dict) and "messages" in output:
            state["messages"].extend(output.get("messages", []))
        elif isinstance(output, dict) and "answer" in output:
            state["messages"].append(AIMessage(content=output["answer"]))

if __name__ == "__main__":
    test_cases = [
        "What was said about 'Running the Disk Defragmenter Program'?",
        "Who is Davido?"
    ]
    for user_input in test_cases:
        response = run_agent(user_input)
        print("\nUser Question:", user_input)
        print("Response:", response)
        print("\n")