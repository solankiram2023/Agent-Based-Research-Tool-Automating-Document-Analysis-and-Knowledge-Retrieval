import os
import json
from typing import List, cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain.tools import tool
from pinecone import Pinecone, Index
from copilotkit.langchain import copilotkit_emit_state, copilotkit_customize_config
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import difflib
import base64
from PIL import Image
from io import BytesIO

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
            index_name = str(file.read())

    pinecone_index = pinecone.Index(str(index_name + "-doc-index"))

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

    # Prepare loading images
    dir_path = os.path.join(os.getcwd(), 'downloads', index_name)

    with open(os.path.join(dir_path, "doc_files_summaries"), 'r', encoding="utf-8") as json_file:
        parsed_json = json.load(json_file)
    
    for i, query in enumerate(queries):
        # Convert queries to embeddings
        query_vector = embeddings.embed_query(query)
        
        # Find relevant chunks in Pinecone
        results = pinecone_index.query(
            vector=[query_vector], 
            top_k=5, 
            include_metadata=True
        )
    
        # If relevant chunks found, append to resources
        for match in results["matches"]:
            resources.append({
                "url": match["id"],
                "title": match["metadata"].get("text", "No title")[:50],
                "description": match["metadata"].get("text", "No description"),
                "vector_resource": True
            })
            
            # Compare the description in resources with summaries in parsed_json
            match_description = match["metadata"].get("text")
            
            # Limit number of images fetched
            image_count = 0
            max_images = 1 

            for document in parsed_json:
                # Check if the description and the summary are similar
                if difflib.SequenceMatcher(None, match_description, document["summary"]).ratio() > 0.6:
                    # If similar, fetch the filename
                    filename = document["filename"]
                    image_path = os.path.join(dir_path, 'tables', filename)
                    print("FILENAME:", filename)

                    # Load the image and convert to base64
                    if os.path.exists(image_path):
                        with open(image_path, "rb") as image_file:
                            image_data = image_file.read()
                            base64_image = base64.b64encode(image_data).decode('utf-8')

                        # Append the base64 image to the resources
                        resources[-1].update({
                            "image_base64": base64_image,
                            "image_filename": filename
                        })

                        # Increment image count
                        image_count += 1

                        # If we've added 2 images, stop adding more
                        if image_count >= max_images:
                            break
                    else:
                        print(f"Image not found: {image_path}")

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
