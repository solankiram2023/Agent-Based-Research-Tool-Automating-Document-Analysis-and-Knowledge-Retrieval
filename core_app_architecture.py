from diagrams import Diagram, Edge, Cluster 
from diagrams.aws.storage import S3 
from diagrams.programming.framework import FastAPI 
from diagrams.custom import Custom 
from diagrams.onprem.client import Users 
from diagrams.programming.framework import React


#     with Cluster("RAG Application", direction = "RL"):
#         streamlit_app << Edge() << users
#         fastapi << Edge() << streamlit_app
#         question << Edge(label="User asks question") << fastapi
#         document_request << Edge(label="Forward request\nto FastAPI") << streamlit_app
#         fastapi << Edge() << document_request
#         fastapi << Edge() << s3_2
#         nvidia << Edge(label="Get Document Summary") >> fastapi
#         pdf2 << Edge(label="Save PDF locally for text, image extraction") << fastapi
#         unstructured << Edge() << pdf2
#         extracted_text << Edge(label="Document Chunks") << unstructured
#         extracted_image << Edge() << unstructured
#         openai_llm1 << Edge(label="Images in Base64 format") << extracted_image
#         openai_embed_1 << Edge(label="Document Chunks") << extracted_text
#         chromadb << Edge(label="Save and Index\nembedded content") << openai_embed_1
#         openai_embed_1 << Edge(label="Image summary") << openai_llm1
#         memory << Edge(label="Store in RAM\nfaster access") << extracted_image
#         openai_embed_2 << Edge() << question
#         mmr << Edge() << openai_embed_2
#         mmr << Edge(label="Relevant Document Chunks") << chromadb
#         mmr << Edge(label="Relevant Images") << memory
#         openai_llm2 << Edge(label="Question with relevant context") << mmr 
#         fastapi << Edge(label="Answer") << openai_llm2
#         cleanlabs << Edge(label="Get Trust Score\nfor LLM response") >> fastapi
#         fastapi << Edge(label="Relevant Images") << memory
#         streamlit_app << Edge(label="Answer or Report\n(with images)") << fastapi
#         users << Edge() << streamlit_app

with Diagram("Core Application Pipeline", show = False):

    # Define nodes
    users           = Users("End Users")
    question        = Custom("Question", "./images/Question.png")
    copilotkit      = React("CopilotKit", ) 
    
    fastapi         = FastAPI("FastAPI")
    openai_embed_1  = Custom("OpenAI\nEmbeddings", "./images/OpenAI.png")
    openai_llm2     = Custom("GPT-4o", "./images/OpenAI.png")

    arxiv_agent    = Custom("Arxiv Agent", "./images/Arxiv.png")
    web_agent      = Custom("Web Agent", "./images/web.png")
    rag_agent      = Custom("RAG Agent", "./images/pinecone.png")

    langgraph       = Custom("LangGraph", "./images/LangGraph.png")

    with Cluster("CoAgent Architecture", direction = "RL"):
        users >> question
        question >> copilotkit
        copilotkit >> fastapi

        fastapi >> langgraph
        langgraph >> fastapi

        fastapi >> copilotkit
        copilotkit >> users

        langgraph >> openai_embed_1
        openai_embed_1 >> langgraph

        langgraph >> openai_llm2
        openai_llm2 >> langgraph

        langgraph >> rag_agent
        rag_agent >> langgraph

        langgraph >> web_agent
        web_agent >> langgraph

        langgraph >> arxiv_agent
        arxiv_agent >> langgraph