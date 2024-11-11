# --- Core application starts here ---

import os
from dotenv import load_dotenv 
from fastapi import FastAPI, status
import uvicorn
import logging
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitSDK, LangGraphAgent
from copilotkit.langchain import copilotkit_messages_to_langchain
from fastapi.responses import JSONResponse

# Custom imports
from agent import graph

# Create a FastAPI app
app = FastAPI()

# Load the environment variables
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console (dev only)
if os.getenv('APP_ENV', "development") == "development":
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Also log to a file
file_handler = logging.FileHandler(os.getenv('FASTAPI_LOG', "fastapi_logs.log"))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler) 

# Register LangGraph agents with CopilotKit
sdk = CopilotKitSDK(
    agents=[
        LangGraphAgent(
            name        = "research_agent",
            description = "Research agent.",
            agent       = graph,
        ),
        LangGraphAgent(
            name                = "research_agent_openai_gpt4o",
            description         = "Research agent.",
            agent               = graph,
            copilotkit_config   = {
                "convert_messages": copilotkit_messages_to_langchain(use_function_call=True)
            }
        ),
    ],
)

# Attach CopilotKit SDK and endpoint to FastAPI
add_fastapi_endpoint(app, sdk, "/copilotkit")

# Route for FastAPI Health check
@app.get("/health")
def health() -> JSONResponse:
    '''Check if the FastAPI application is setup and running'''

    logger.info("GET - /health request received")
    return JSONResponse({
        'status'    : status.HTTP_200_OK,
        'type'      : "string",
        'message'   : "You're viewing a page from FastAPI"
    })


def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

if __name__  == "__main__":
    main()
