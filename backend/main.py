# --- Core application starts here ---

import os
from dotenv import load_dotenv 
from fastapi import FastAPI, status, Request
import uvicorn
import logging
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitSDK, LangGraphAgent
from copilotkit.langchain import copilotkit_messages_to_langchain
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Custom imports
from agent import graph
from services import generate_markdown_for_document, convert_markdown_to_pdf, export_and_serve_codelab

# Create a FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins       = ["*"],
    allow_credentials   = True,
    allow_methods       = ["*"],
    allow_headers       = ["*"],
)

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

class MarkdownReport(BaseModel):
    content: str

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

# Route for setting up Pinecone index as source
@app.post("/sourcedocument")
async def set_source(request: Request):
    ''' Set the document ID of the source document '''

    document_info = await request.json()
    with open("sourcedocument", 'w', encoding='utf-8') as file:
        file.write(str(document_info['documentId']))

@app.post("/exportPDF")
async def exportToPDF(request: Request):
    ''' Export the report to PDF '''

    output_filepath = os.path.join(os.getcwd(), "output.pdf")

    with open("sourcedocument", 'r', encoding='utf-8') as file:
        document_id = str(file.read())
        generate_markdown_for_document(document_id)
        convert_markdown_to_pdf()

        if os.path.exists(output_filepath):
            return FileResponse(
                path = output_filepath,
                media_type = "application/json",
                filename = "output.pdf"
            )
        
@app.post("/exportCodelabs")
async def exportToCodelabs():
    ''' Export markdown content to codelabs '''
    export_and_serve_codelab()

def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

if __name__  == "__main__":
    main()
