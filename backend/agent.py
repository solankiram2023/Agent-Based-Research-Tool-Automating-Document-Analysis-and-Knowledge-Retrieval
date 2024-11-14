# --- This is the main entry point for the AI ---
# --- It defines the workflow graph and the entry point for the agent ---

from typing import cast
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Custom imports
from state import AgentState
from download import download_node
from chat import chat_node
from search import search_node
from delete import delete_node, perform_delete_node
from retrieve import retrieve_node

# Define a new graph
workflow = StateGraph(AgentState)
workflow.add_node("download", download_node)
workflow.add_node("chat_node", chat_node)
workflow.add_node("search_node", search_node)
workflow.add_node("delete_node", delete_node)
workflow.add_node("perform_delete_node", perform_delete_node)
workflow.add_node("retrieve_node", retrieve_node)

def route(state):
    """Route after the chat node."""

    messages = state.get("messages", [])
    
    if messages and isinstance(messages[-1], AIMessage):
        ai_message = cast(AIMessage, messages[-1])


        if ai_message.tool_calls:
            print("Calling tool: ", ai_message.tool_calls[0]["name"])

        if ai_message.tool_calls and ai_message.tool_calls[0]["name"] == "RetrieveFromPinecone":
            return "retrieve_node"

        # If user response is negative, fall back to web search
        if ai_message.tool_calls and ai_message.tool_calls[0]["name"] == "Search":
            return "search_node"
        
        # Remove resources if user asks for it
        if ai_message.tool_calls and ai_message.tool_calls[0]["name"] == "DeleteResources":
            return "delete_node"
    
    # Handover to chat_node to handle routing logic
    if messages and isinstance(messages[-1], ToolMessage):
        return "chat_node"

    return END

# Conversation memory (temporary memory)
memory = MemorySaver()

# Connect the nodes
workflow.set_entry_point("download")
workflow.add_edge("download", "chat_node")
workflow.add_conditional_edges("chat_node", route, ["retrieve_node", "search_node", "chat_node", "delete_node", END])
workflow.add_edge("delete_node", "perform_delete_node")
workflow.add_edge("perform_delete_node", "chat_node")
workflow.add_edge("search_node", "download")
workflow.add_edge("retrieve_node", "chat_node")

# Create workflow graph
graph = workflow.compile(checkpointer=memory, interrupt_after=["delete_node"])
