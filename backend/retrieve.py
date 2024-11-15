import os
import time
from typing import List, cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain.tools import tool
from pinecone import Pinecone, Index
from copilotkit.langchain import copilotkit_emit_state, copilotkit_customize_config
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

# Custom imports
from state import AgentState

load_dotenv()

@tool
def RetrieveFromPinecone(queries: List[str]):
    """Retrieve documents from Pinecone based on the user's query."""

async def retrieve_node(state: AgentState, config: RunnableConfig):
    """Retrieve relevant documents from Pinecone."""

    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{
            "state_key"     : "research_question",
            "tool"          : "WriteResearchQuestion",
            "tool_argument" : "research_question",
        }],
        emit_tool_calls="WriteResearchQuestion"
    )

    pinecone = Pinecone(api_key = os.getenv("PINECONE_API_KEY"))

    # Load Pinecone Index
    index_name = None
    
    if os.path.isfile("sourcedocument"):
        with open("sourcedocument", 'r', encoding='utf-8') as file:
            index_name = str(file.read()) + "-doc-index"

    pinecone_index = pinecone.Index(index_name)

    ai_message = cast(AIMessage, state["messages"][-1])
    state["resources"] = state.get("resources", [])
    state["logs"] = state.get("logs", [])
    
    # Fetch the list of queries returned by the LLM model
    queries = ai_message.tool_calls[0]["args"]["queries"]
    resources = []

    # Broadcast received queries to frontend
    for query in queries:
        state["logs"].append({
            "message"   : f"Search PDF document for {query}",
            "done"      : False
        })
    await copilotkit_emit_state(config, state)

    embeddings = OpenAIEmbeddings(
        model   = "text-embedding-3-large", 
        api_key = os.getenv("OPENAI_API_KEY")
    )
    
    for i, query in enumerate(queries):

        # Convert queries to embeddings
        query_vector = embeddings.embed_query(query)
        
        # Find relevant chunks in Pinecone
        results = pinecone_index.query(
            vector = [query_vector], 
            top_k  = 5, 
            include_metadata=True
        )
        
        # If relevant chunks found, append to resources
        for match in results["matches"]:
            resources.append({
                "url"           : match["id"],
                "title"         : match["metadata"].get("text", "No title")[:50],
                "description"   : match["metadata"].get("text", "No description"),
                "vector_resource" : True
            })

        # Add to state if relevant context was found
        if resources:
            state["resources"].extend(resources)
        
        # Broadcast status to frontend
        state["logs"][i]["done"] = True
        await copilotkit_emit_state(config, state)

    # Add to state if relevant context was found
    if resources:
        state["resources"].extend(resources)

    state["messages"].append(ToolMessage(
        tool_call_id = ai_message.tool_calls[0]["id"],
        content      = f"Added relevant chunks from Pinecone: {resources}"
    ))

    state["logs"] = []

    return state
