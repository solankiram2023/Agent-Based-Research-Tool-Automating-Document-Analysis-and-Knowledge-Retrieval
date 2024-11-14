import os
import logging
from dotenv import load_dotenv
from fastapi import status
from fastapi.responses import JSONResponse
from snowflake.connector import DictCursor
from connectDB import create_connection_to_snowflake, close_connection

# Helper function to create Arxiv Agent
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from xml.etree import ElementTree

# Helper function to create Web Search Agent
from serpapi import GoogleSearch
from dotenv import load_dotenv
import os
from getpass import getpass
from langchain_core.tools import tool


# Load env variables
load_dotenv()


# logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# Logger configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console (dev only)
if os.getenv('APP_ENV') == "development":
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Also log to a file
file_handler = logging.FileHandler(os.getenv('FASTAPI_LOG_FILE', "fastapi_errors.log"))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler) 

# Helper function to get the list of documents
def explore_documents(prompt_count):
    logger.info(f"FASTAPI Services - explore_documents() - Listing out the documents")
    conn = create_connection_to_snowflake()

    if conn is None:
        return JSONResponse({
            'status': status.HTTP_503_SERVICE_UNAVAILABLE,
            'type': 'string',
            'message': 'Database not found'
        })
    
    if conn:
        logger.info(f"FASTAPI Services - explore_documents() - Database connection successful")
        cursor = conn.cursor(DictCursor)
        try:
            logger.info(f"FASTAPI Services - SQL - explore_documents() - Executing SELECT statement")
            query = """
            SELECT document_id, title, image_url, FROM publications_info WHERE document_id IN (%s)
            """

            document_ids = ['68db7e4f057f494fb5b939ba258cefcd', '97b6383e18bb48d1b7daceb27ad0a198', '52af53cc2f5e42558253aa572a55b78a']
            cursor.execute(query, (document_ids,))
            rows = cursor.fetchall()
            logger.info(f"FASTAPI Services - SQL - explore_documents() - Output - {rows}")

            response = {
                    'status'    : status.HTTP_200_OK,
                    'type'      : "json",
                    'message'   : [{"document_id": row["DOCUMENT_ID"], "title": row['TITLE'], "image_url": row['IMAGE_URL']} for row in rows],
                    'length'    : prompt_count
            }

            logger.info(f"FASTAPI Services - SQL - explore_documents() - SELECT statement executed successfully")
            
            return JSONResponse(content = response)

        except Exception as e:
            logger.error(f"FASTAPI Services Error - explore_documents() encountered an error: {e}")  

        finally:
            close_connection(conn, cursor)
            logger.info(f"FASTAPI Services - explore_documents() - Database - Connection to the database was closed")


        return JSONResponse({
            'status'    : status.HTTP_500_INTERNAL_SERVER_ERROR,
            'type'      : "string",
            'message'   : "Could not fetch the list of prompts. Something went wrong."
        })

# Helper function to load the document
def load_document(document_id):
    logger.info(f"FASTAPI Services - load_document() - Loading the user selected document")
    conn = create_connection_to_snowflake()

    if conn is None:
        return JSONResponse({
            'status': status.HTTP_503_SERVICE_UNAVAILABLE,
            'type': 'string',
            'message': 'Database not found'
        })
    
    if conn:
        logger.info(f"FASTAPI Services - load_document() - Database connection successful")
        cursor = conn.cursor()
        try:
            logger.info(f"FASTAPI Services - SQL - load_document() - Executing SELECT statement")
            query = """
            SELECT * FROM publications_info WHERE document_id = %s;
            """
            cursor.execute(query, (document_id,))
            record = cursor.fetchone()
            logger.info(f"FASTAPI Services - SQL - load_document() - SELECT statement executed successfully")

            if record is None:
                close_connection(conn, cursor)
                logger.info("FASTAPI Services - Database - load_document() - Connection to the database was closed")
                return JSONResponse(
                    {
                        'status'  : status.HTTP_404_NOT_FOUND,
                        'type'    : 'string',
                        'message' : f"Could not fetch the details for the given document_id {document_id}"
                    }
                )
            close_connection(conn, cursor)
            logger.info(f"FASTAPI Services - load_document() - Database - Connection to the database was closed")

            return JSONResponse({
                'status' : status.HTTP_200_OK,
                'type'   : 'json',
                'message': record
            })                       

        except Exception as e:
            logger.error(f"FASTAPI Services Error - load_document() encountered an error: {e}")  

        finally:
            close_connection(conn, cursor)
            logger.info(f"FASTAPI Services - load_document() - Database - Connection to the database was closed")

        return JSONResponse({
            'status'    : status.HTTP_500_INTERNAL_SERVER_ERROR,
            'type'      : "string",
            'message'   : "Could not fetch the user selected document. Something went wrong."
        })
    

# Extract relevant keywords from user's question using a GPT model
def extract_keywords_from_question(question: str) -> str:
    """Extracts relevant 5 keywords or topics from the user's question."""
    logger.info(f"FASTAPI Services - extract_keywords_from_question() - Extracts relevant keywords based on users question")
    
    # Define a prompt template for keyword extraction (you can modify this based on your use case)
    prompt_template = """
    Given the following question, return a list of 5 relevant keywords or topics to search in research papers:
    Question: {question}
    Relevant Keywords/Topics (5):
    """
    
    # Initialize the LLM (e.g., OpenAI's GPT-3/4) for keyword extraction
    logger.info(f"FASTAPI Services - extract_keywords_from_question() - Initialize OpenAI Agent to extract keywords")
    llm = ChatOpenAI(model="gpt-4o", api_key = os.getenv("OPENAI_API_KEY"))
    prompt = PromptTemplate(input_variables=["question"], template=prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)
    logger.info(f"FASTAPI Services - extract_keywords_from_question() - LLM Chain Agent initialized successfully")
    
    # Extract the keywords/topics from the question
    keywords = chain.run(question)
    
    # Return the keywords (clean it if necessary)
    logger.info(f"FASTAPI Services - extract_keywords_from_question() - Keywords extracted and returning them to main")
    return keywords.strip()

# Function to search Arxiv for relevant articles based on extracted keywords
def search_arxiv(keywords: str, max_results: int = 5):
    """Searches Arxiv for papers related to the given keywords."""
    logger.info(f"FASTAPI Services - search_arxiv() - Searches Arxiv for papers related to the given keywords.")

    search_url = f"http://export.arxiv.org/api/query?search_query=all:{keywords}&start=0&max_results={max_results}"
    
    # Send the request to ArXiv's API
    logger.info(f"FASTAPI Services - search_arxiv() - Request sent to Arxiv Agent API")
    response = requests.get(search_url)
    
    # Parse the XML response
    if response.status_code == 200:
        logger.info(f"FASTAPI Services - search_arxiv() - Request successful, Response generated")

        result = response.text

        # Parse the XML using ElementTree
        root = ElementTree.fromstring(result)
        # Namespaces used in Arxiv's API responses
        namespaces = {'': 'http://www.w3.org/2005/Atom'}
        # Find all entries in the feed
        entries = root.findall('.//entry', namespaces)

        # Get the top articles and package the relevant information
        articles = []

        logger.info(f"FASTAPI Services - search_arxiv() - Looping through entries in the response generated")
        for entry in entries[:max_results]:
            title = entry.find('title', namespaces).text
            arxiv_id = entry.find('id', namespaces).text
            summary = entry.find('summary', namespaces).text
            
            articles.append({
                'title': title,
                'arxiv_id': arxiv_id.split('/')[-1], 
                'abstract': summary
            })

        logger.info(f"FASTAPI Services - search_arxiv() - Contents like title, arxiv_id, summary of every research article is stored in a dictionary and returning it to main")
        return articles
    else:
        logger.info(f"FASTAPI Services - search_arxiv() - Request to Arxiv API failed")
        return None

# Helper function to create Arxiv Agent
@tool("arxiv_agent")
def arxiv_agent(question: str):
    """Fetches relevant ArXiv papers based on a user question."""
    logger.info(f"FASTAPI Services - arxiv_agent() - Fetches relevant ArXiv papers based on a user question.")
    
    try:
        # Step 1: Extract keywords from the user's question
        keywords = extract_keywords_from_question(question)
        logger.info(f"FASTAPI Services - arxiv_agent() - Keywords extracted successfully")
        if not keywords:
            logger.info(f"FASTAPI Services - arxiv_agent() - Couldn't extract keywords from the question")
            return JSONResponse(
                        {
                            'status'  : status.HTTP_404_NOT_FOUND,
                            'type'    : 'string',
                            'message' : f"Sorry, I couldn't extract any relevant keywords from your question: {question}"
                        }
                    )
        
        logger.info(f"FASTAPI Services - arxiv_agent() - Question  = {question} \n Relevant keywords = \n{keywords}")
        
        # Step 2: Search ArXiv using the extracted keywords
        logger.info(f"FASTAPI Services - arxiv_agent() - Calling Arxiv agent to search relevant research papers for the keywords")
        results = search_arxiv(keywords)
        
        # Step 3: Return results in a user-friendly format
        if results:
            logger.info(f"FASTAPI Services - arxiv_agent() - Relevant research papers found")

            formatted_results = []
            for idx, result in enumerate(results):
                formatted_results.append({
                    "ArXiv ID": result['arxiv_id'],
                    "Title": result['title'],
                    "Abstract": result['abstract'],
                    'Link': f"https://export.arxiv.org/abs/{result['arxiv_id']}"
                })
            logger.info(f"FASTAPI Services - arxiv_agent() - Response generated with data: {formatted_results}")
            return JSONResponse({
                'status' : status.HTTP_200_OK,
                'type'   : 'json',
                'message': formatted_results
            }) 
        else:
            logger.info(f"FASTAPI Services - arxiv_agent() - No relevant research papers found on Arxiv")
            return JSONResponse(
                        {
                            'status'  : status.HTTP_404_NOT_FOUND,
                            'type'    : 'string',
                            'message' : f"Sorry, no relevant papers were found on ArXiv for your question: {question}"
                        }
                    )
    except Exception as e:
        logger.error(f"FASTAPI Services Error - arxiv_agent() encountered an error: {e}") 
        return JSONResponse(
            {
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'type': 'string',
                'message': f"An error occurred while processing the request: {str(e)}"
            }
        ) 

# Helper function to create Web Search Agent
@tool("web_search")
def web_search(query: str):
    """Finds general knowledge information related to PDFs using Google search."""
    logger.info(f"FASTAPI Services - web_search() - Fetches relevant ArXiv papers based on a user question.")

    try:
        # SerpAPI parameters (assumes you've set the SERPAPI_KEY in your environment variables)
        logger.info(f"FASTAPI Services - web_search() - SerpAPI parameters set")
        serpapi_params = {
            "engine": "google",
            "api_key": os.getenv("SERPAPI_KEY")
        }

        # Modify the query to target PDF documents
        pdf_query = f"{query} filetype:pdf"
        # query = f"{query}"
        
        # Search using SerpAPI with the PDF-targeting query
        logger.info(f"FASTAPI Services - web_search() - Searching using SerpAPI for question: {query}")
        search = GoogleSearch({
            **serpapi_params,
            "q": pdf_query,
            "num": 5
        })
        
        # Get the organic results from the search
        results = search.get_dict().get("organic_results", [])
        logger.info(f"FASTAPI Services - web_search() - SearAPI Results fetched successfully")
        
        if not results:
            logger.info(f"FASTAPI Services - web_search() - No relevant results found")
            return JSONResponse(
                    {
                        'status'  : status.HTTP_404_NOT_FOUND,
                        'type'    : 'string',
                        'message' : f"Sorry, no results by SerpAPI for your question: {query}"
                    }
                )
        
        # Format the results in a user-friendly way
        contexts = "\n---\n".join(
            [f"Title: {x['title']}\nSnippet: {x['snippet']}\nLink: {x['link']}" for x in results]
        )

        formatted_context = []

        for x in results:
            formatted_context.append({
                "Title": x['title'],
                "Context": x['snippet'],
                "Link": x['link']
            })

        logger.info(f"FASTAPI Services - web_search() - Relevant results found by Web Search Agent for query = {query} are {formatted_context}")
        return JSONResponse({
                    'status' : status.HTTP_200_OK,
                    'type'   : 'json',
                    'message': formatted_context
                }) 
    except Exception as e:
        logger.error(f"FASTAPI Services Error - web_search() encountered an error: {e}") 
        return JSONResponse(
            {
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'type': 'string',
                'message': f"An error occurred while processing the request: {str(e)}"
            }
        ) 