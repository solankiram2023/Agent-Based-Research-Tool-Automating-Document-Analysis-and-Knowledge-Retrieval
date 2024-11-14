import logging
from dotenv import load_dotenv
from fastapi import APIRouter, status, Depends
from models import ExploreDocs, LoadDocument, ArxivAgent_Prompt
from fastapi.responses import JSONResponse

# Importing all the necessary functions
from services import explore_documents, load_document, arxiv_agent, web_search

router = APIRouter()

# Load env variables
load_dotenv()

# Logger configuration
logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# Route for FastAPI Health check
@router.get("/")
def health() -> JSONResponse:
    '''Check if the FastAPI application is setup and running'''

    logger.info("GET - /health request received")
    return JSONResponse({
        'status'    : status.HTTP_200_OK,
        'type'      : "string",
        'message'   : "You're viewing a page from FastAPI"
    })


# Route for Exploring Documents
@router.get("/exploredocs",
            response_class = JSONResponse,
            responses = {
                401: {'description': 'Invalid or expired token'},
                402: {'description': 'Insufficient permissions'},
                403: {'description': 'Returns a list of documents'}
            }
        )
def explore_docs(
    prompt: ExploreDocs = Depends(),
    # token: str = Depends(verify_token)
) -> JSONResponse:
    logger.info("FASTAPI Routers - explore docs = Route for fetching the list of documents")
    if prompt.count is None:
        logger.info(f"FASTAPI Routers - explore_docs - GET - /exploredocs? request received")
        prompt.count = 3
    else:
        logger.info(f"FASTAPI Routers - explore_docs - GET - /exploredocs?count={prompt.count} request received")
    return explore_documents(prompt.count)



# Route for Selecting a document
@router.get("/load_docs/{document_id}",
        response_class = JSONResponse,
        responses = {
            401: {'description': 'Invalid or expired token'},
            402: {'description': 'Insufficient permissions'},
            403: {'description': 'Returns all available data about a task id'}
        }
    )
def load_docs(
    input_id: LoadDocument = Depends(),
    # token: str = Depends(verify_token)
) -> JSONResponse:
    
    logger.info("FASTAPI Routers - load_docs = Route for fetching selected document")
    logger.info(f"FASTAPI Routers - load_docs = GET - /load_docs/{input_id.document_id} request received")
    logger.info(f"FASTAPI Routers - load_docs = Loading the entire document with id = {input_id.document_id}")
    return load_document(input_id.document_id)


# Route for Arxiv Agent
@router.get("/arxiv_agent/{question}",
        response_class=JSONResponse,
        responses = {
            401: {'description': 'Invalid or expired token'},
            402: {'description': 'Insufficient permissions'},
            403: {'description': 'Returns all available data about a task id'}
        }
    )
def arxiv_research_papers(
    question: str,
) -> JSONResponse:
    logger.info("FASTAPI Routers - arxiv_agent = Route for Arxiv Agent")
    logger.info(f"FASTAPI Routers - arxiv_agent = GET - /arxiv_agent/{question} request received")
    logger.info(f"FASTAPI Routers - arxiv_agent = Retrieving relevant research papers with question prompt")
    return arxiv_agent(question)


# Route for Web Search Agent
@router.get("/websearch_agent/{question}",
        response_class=JSONResponse,
        responses = {
            401: {'description': 'Invalid or expired token'},
            402: {'description': 'Insufficient permissions'},
            403: {'description': 'Returns all available data about a task id'}
        }
    )
def websearch_results(
    question: str,
) -> JSONResponse:
    logger.info("FASTAPI Routers - arxiv_agent = Route for Arxiv Agent")
    logger.info(f"FASTAPI Routers - arxiv_agent = GET - /arxiv_agent/{question} request received")
    logger.info(f"FASTAPI Routers - arxiv_agent = Retrieving relevant research papers with question prompt")
    return web_search(question)