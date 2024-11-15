import os
import time
import logging
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector import Error
import markdown
from weasyprint import HTML
import subprocess

# Load all environment variables
load_dotenv()

# Logger configuration
logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_connection_to_snowflake(attempts = 3, delay = 2):

    logger.info("FASTAPI - create_connection() - Creating connection to Snowflake database")

    user        = os.getenv("DB_USERNAME", None),
    password    = os.getenv("DB_PASSWORD", None),
    account     = os.getenv("DB_ACCOUNT", None),
    warehouse   = os.getenv("DB_WAREHOUSE", None),
    database    = os.getenv("DB_NAME", None),
    schema      = os.getenv("DB_SCHEMA", None),
    role               = os.getenv("DB_USER_ROLE", None)

    if not (user and password and account and warehouse and database and schema and role):
        logger.error("FASTAPI - create_connection() - Environment variables contain 'None' values")
        return None

    # Create connection with Snowflake Database
    attempt = 1
    while attempt < attempts:
        try:
            conn = snowflake.connector.connect(
                user        = os.getenv("DB_USERNAME", None),
                password    = os.getenv("DB_PASSWORD", None),
                account     = os.getenv("DB_ACCOUNT", None),
                warehouse   = os.getenv("DB_WAREHOUSE", None),
                database    = os.getenv("DB_NAME", None),
                schema      = os.getenv("DB_SCHEMA", None),
                role        = os.getenv("DB_USER_ROLE", None)
            )

            logger.info("FASTAPI - create_connection() - Connection to Snowflake database established successfully")
            return conn
        
        except (Error, IOError) as e:
            if attempt == attempts:
                logger.error(f"FASTAPI - create_connection() - Failed to connect to the Snowflake Database: {e}")
                return None
            else:
                logger.warning(f"FASTAPI - create_connection() - Connection Failed: {e} - Retrying {attempt}/{attempts}")
                time.sleep(delay ** attempt)
                attempt += 1
    return None

def close_connection(dbconn, cursor = None):
    logger.info(f"FASTAPI - close_connection() - Closing the database connection")
    try:
        if dbconn is not None:
            cursor.close()
            dbconn.close()
            logger.info(f"FASTAPI - close_connection() - {dbconn} conn closed successfully")
        else:
            logger.warning(f"FASTAPI - create_connection() - {dbconn} connection does not exist")
    except Exception as e:
        logger.error(f"FASTAPI - close_connection() - Error while closing the database connection: {e}")

def save_response_to_db(document_id, question, response):
    logger.info(f"FASTAPI Services - save_response_to_db() - Saving Research Notes to SnowFlake database")
    
    conn = create_connection_to_snowflake()
    status = False
   
    if conn:
        logger.info(f"FASTAPI Services - save_response_to_db() - Database connection successful")
        cursor = conn.cursor()
        
        try:
            logger.info(f"FASTAPI Services - SQL - save_response_to_db() - Executing INSERT statement")
            
            query = f"""
            INSERT INTO AGENTRESPONSES(DOCUMENT_ID, QUESTION, RESPONSE) 
            VALUES('{document_id}', '{str(question).replace("'", "")}', '{str(response).replace("'", "")}')
            """

            cursor.execute(query)
            conn.commit()
            logger.info(f"FASTAPI Services - SQL - save_response_to_db() - INSERT statement executed successfully")
            status = True

        except Exception as e:
            logger.error(f"FASTAPI Services Error - save_response_to_db() encountered an error: {e}")  
            
        finally:
            close_connection(conn, cursor)
            logger.info(f"FASTAPI Services - save_response_to_db() - Database - Connection to the database was closed")

    return status

def fetch_agent_responses(doc_id):
    conn = create_connection_to_snowflake()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        query = f"""
        SELECT QUESTION, RESPONSE
        FROM PUBLICATIONS.PUBLIC.AGENTRESPONSES
        WHERE DOCUMENT_ID = '{doc_id}'
        """
        cursor.execute(query)
        results = cursor.fetchall()
        logger.info(f"Fetched {len(results)} rows for DOCUMENT_ID: {doc_id}")
        
        return results
    
    except Exception as e:
        logger.error(f"Error fetching data for DOCUMENT_ID {doc_id}: {e}")
        return []
    
    finally:
        close_connection(conn, cursor)

def write_to_markdown(doc_id, responses):
    try:
        
        with open(f"document.md", "w") as file:
            
            for i, (question, response) in enumerate(responses, 1):
                file.write(f"# Question {i}\n")
                file.write(f"## Question: {question}\n")
                file.write(f"##Response: \n")
                file.write(f"{response}\n\n")
        
        logger.info(f"Markdown file for DOCUMENT_ID {doc_id} created successfully.")
    
    except Exception as e:
        logger.error(f"Error writing to markdown file for DOCUMENT_ID {doc_id}: {e}")

def generate_markdown_for_document(doc_id):
    responses = fetch_agent_responses(doc_id)
    
    if responses:
        write_to_markdown(doc_id, responses)
    else:
        logger.warning(f"No responses found for DOCUMENT_ID {doc_id}")

def convert_markdown_to_pdf():
    
    input_filepath = os.path.join(os.getcwd(), "document.md")
    output_filepath = os.path.join(os.getcwd(), "output.pdf")
    
    # Read Markdown file
    with open(input_filepath, 'r') as f:
        markdown_text = f.read()

    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_text)

    css = """
    <style>
        img { max-width: 100%; height: auto; }
    </style>
    """

    html_content = html_content + css

    # Convert HTML to PDF with WeasyPrint
    HTML(
        string   = html_content, 
        base_url = os.path.dirname(input_filepath)
    ).write_pdf(output_filepath)
    
    print(f"PDF file created successfully at {output_filepath}")

def export_and_serve_codelab():
    input_file = os.path.join(os.getcwd(), "document.md")
    
    # Define metadata for the Codelab
    metadata = """
summary: How to Write a Codelab
id: codelab-export-agent
categories: Sample
tags: medium
status: Published 
authors: Zarin
Feedback Link: https://zarin.io

"""

    with open(input_file, 'r', encoding='utf-8') as f:
        original_markdown = f.read()

    # Combine metadata with the original markdown content
    new_markdown_content = metadata + original_markdown

    # Save the modified markdown to a temporary file
    modified_input_file = os.path.join(os.getcwd(), "document_with_metadata.md")
    with open(modified_input_file, 'w', encoding='utf-8') as f:
        f.write(new_markdown_content)
    
    export_command = ["C:\\Users\\Pigeon\\go\\bin\\claat", "export", modified_input_file]
    print(f"Running: {' '.join(export_command)}")
    result = subprocess.run(export_command, capture_output=True, text=True)
    
    # Check if export was successful
    if result.returncode == 0:
        print("Export successful")
        
        output_dirs = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d)]
        

        codelab_path = os.path.join(os.getcwd(), "codelab-export-agent")
        # codelab_path = None
        # for directory in output_dirs:
        #     if directory != os.getcwd():
        #         codelab_path = os.path.join(os.getcwd(), directory)
        
        # Check for the Codelab path
        if codelab_path and os.path.exists(codelab_path):
            os.chdir(codelab_path)
            print(f"Serving Codelab from: {codelab_path}")
            
            # Run the claat serve command
            serve_command = ["C:\\Users\\Pigeon\\go\\bin\\claat", "serve", "-addr", "localhost:9000"]
            print(f"Running: {' '.join(serve_command)}")
            subprocess.run(serve_command)
        
        else:
            print("Error: Could not find the generated Codelab directory.")
    else:
        print("Export failed")
        print(result.stderr)
