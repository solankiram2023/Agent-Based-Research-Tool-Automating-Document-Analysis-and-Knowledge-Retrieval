import os
import time
from typing import List, cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain.tools import tool
from copilotkit.langchain import copilotkit_emit_state, copilotkit_customize_config
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from xml.etree import ElementTree
import requests
import warnings

# Suppress deprecation warning
warnings.filterwarnings('ignore')

# Custom imports
from state import AgentState

load_dotenv()

@tool
def lookupArxiv(queries: List[str]):
    """Retrieve documents from Pinecone based on the user's query."""

# Extract relevant keywords from user's question using a GPT model
def extract_keywords_from_question(question: str) -> str:
    """Extracts relevant 5 keywords or topics from the user's question."""
    
    # Define a prompt template for keyword extraction (you can modify this based on your use case)
    prompt_template = """
    Given the following question, return a list of 5 relevant keywords or topics to search in research papers:
    Question: {question}
    Relevant Keywords/Topics (5):
    """
    
    # Initialize the LLM (e.g., OpenAI's GPT-3/4) for keyword extraction
    llm = ChatOpenAI(
        model   = "gpt-4o", 
        api_key =  os.getenv("OPENAI_API_KEY")
    )
    prompt = PromptTemplate(
        input_variables = ["question"], 
        template        = prompt_template
    )
    chain = LLMChain(
        llm     = llm, 
        prompt  = prompt
    )
    
    # Extract the keywords/topics from the question
    keywords = chain.run(question)
    
    # Return the keywords (clean it if necessary)
    return keywords.strip()

def search_arxiv(keywords: str, max_results: int = 5):
    """Searches Arxiv for papers related to the given keywords."""

    search_url = f"http://export.arxiv.org/api/query?search_query=all:{keywords}&start=0&max_results={max_results}"
    
    # Send the request to ArXiv's API
    response = requests.get(search_url)
    
    # Parse the XML response
    if response.status_code == 200:

        result = response.text

        # Parse the XML using ElementTree
        root = ElementTree.fromstring(result)
        
        # Namespaces used in Arxiv's API responses
        namespaces = {'': 'http://www.w3.org/2005/Atom'}
        
        # Find all entries in the feed
        entries = root.findall('.//entry', namespaces)

        # Get the top articles and package the relevant information
        articles = []

        for entry in entries[:max_results]:
            title = entry.find('title', namespaces).text
            arxiv_id = entry.find('id', namespaces).text
            summary = entry.find('summary', namespaces).text
            
            articles.append({
                'title'     : title,
                'arxiv_id'  : arxiv_id.split('/')[-1], 
                'abstract'  : summary
            })
        
        return articles
    
    else:
        return None


async def arxiv_node(state: AgentState, config: RunnableConfig):
    """Retrieve relevant documents from Pinecone."""

    ai_message = cast(AIMessage, state["messages"][-1])
    
    state["logs"] = state.get("logs", [])
    state["resources"] = state.get("resources", [])
    state["arvix_papers"] = state.get("arxiv_papers", [])

    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{
            "state_key"     : "report",
            "tool"          : "WriteReport",
            "tool_argument" : "report",
        }, {
            "state_key"     : "research_question",
            "tool"          : "WriteResearchQuestion",
            "tool_argument" : "research_question",
        }],
        emit_tool_calls="WriteResearchQuestion"
    )
    
    # Fetch the list of queries returned by the LLM model
    query = ai_message.tool_calls[0]["args"]["queries"]
    resources = []

    # Broadcast received queries to frontend
    state["logs"].append({
        "message"   : f"Searching Arxiv Repository for research papers related to {query}",
        "done"      : False
    })
    await copilotkit_emit_state(config, state)

    try:
        # Step 1: Extract keywords from the user's question
        keywords = extract_keywords_from_question(query)
        
        if keywords:
            state["logs"].append({
                "message"   : f"Extracted keywords: {keywords}",
                "done"      : True
            })
            await copilotkit_emit_state(config, state)
            
            # Step 2: Search ArXiv using the extracted keywords
            results = search_arxiv(keywords)
            
            # Step 3: Return results in defined format
            if results:

                for _, result in enumerate(results):

                    state["logs"].append({
                        "message"   : f"Found Arxiv Research Paper {result['title']}",
                        "done"      : True
                    })
                    await copilotkit_emit_state(config, state)
                    
                    resources.append({
                        "title"         : result['title'],
                        "description"   : result['abstract'],
                        'url'           : f"https://export.arxiv.org/abs/{result['arxiv_id']}"
                    })
        
    except Exception as e:
        print("Exception occurred in arxiv agent: ", e)

    state["arvix_papers"].extend(resources)
    state["resources"].extend(resources)

    # Broadcast status to frontend
    state["logs"][0]["done"] = True
    await copilotkit_emit_state(config, state)

    state["messages"].append(ToolMessage(
        tool_call_id = ai_message.tool_calls[0]["id"],
        content      = f"Added relevant arxiv results: {resources}"
    ))

    return state
