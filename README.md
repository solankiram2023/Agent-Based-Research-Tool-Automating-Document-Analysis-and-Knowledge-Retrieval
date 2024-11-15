# Assignment4

## Agent-Based Research Tool: Automating Document Analysis and Knowledge Retrieval
An interactive, agent-based research application built using FastAPI, Coagents, and Langraph to analyze and explore publications. The application parses document contents—including text, tables, images, and graphs—using Docling and stores structured data as vector embeddings in Pinecone for scalable similarity search. Users can interactively explore selected documents, query research insights, and retrieve responses leveraging multi-agent capabilities such as Arxiv search, web search, and Retrieval-Augmented Generation (RAG).

The tool enables robust Q/A functionality, real-time document selection, and multi-step workflows for comprehensive research. It supports professional reporting by exporting results to templated PDF files and structured Codelabs documentation, enhancing usability and facilitating knowledge discovery. This end-to-end system empowers researchers with an automated, efficient, and interactive solution for document-based research and analysis.


## Live Application Link
- CoAgent application link: http://18.219.124.78:3000/
- FastAPI: http://18.219.124.78:8000/docs
- CodeLabs Link: http://18.219.124.78:9000/

## Codelabs Link
Codelabs documentation link: https://codelabs-preview.appspot.com/?file_id=1qFJkJYuKjS6lhUt_rgpfV4QB3Ic7YJtiIAI4vZ_7vW0#0

## Demo Link
Demo Link is attached in Codelabs Document

## Attestation and Team Contribution
**WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK**

Name | NUID | Contribution% | Work_Contributed
--- | --- | --- | --- |
Sandeep Suresh Kumar | 002841297 | 33% | RAG Agent with Langgraph, Coagents, Deployment
Deepthi Nasika       | 002474582 | 33% | Docling Parsing, Vector Storage, Export to Codelabs
Gomathy Selvamuthiah | 002410534 | 33% | Airflow Pipeline, Web Search Agent, Export to PDF
Ramy Solanki         | 002816593 | 33% | Llama Index Agent, Arxiv Agent, Dockerization

## Problem Statement
This project aims to address these challenges by creating an agent-based research tool that leverages Retrieval-Augmented Generation (RAG) and multi-agent systems to enable users to interact seamlessly with document content. By incorporating advanced technologies like Langraph and Pinecone, the application simplifies research processes and empowers users to derive accurate, context-aware insights. The application primarily focuses on:

1. Content Parsing and Vector Storage: Parse document contents, including text, tables, images, and graphs, using Docling and store vectorized embeddings in Pinecone for scalable similarity search.
2. Automated Workflow with Airflow: Automate document parsing, embedding generation, and vector storage through a robust Airflow pipeline.
3. Multi-Agent System for Research: Enable document exploration, Arxiv-based paper searches, web-based contextual searches, and Q&A functionality using Langraph’s multi-agent capabilities.
4. Interactive User Interface: Provide a user-friendly interface with Coagents or Streamlit for document selection, querying, and real-time interaction.
5. Comprehensive Reports: Generate professional reports in PDF and Codelabs formats containing responses, images, and graphs relevant to user queries.
6. Efficient Workflow Management: Validate and store research notes, enabling incremental indexing and efficient future searches.




## Architecture Diagram
### 1. Core Application Pipeline
![Architecture Diagram]()



### 2. Airflow Pipeline
![Architecture Diagram](https://github.com/BigDataIA-Fall2024-TeamB6/Assignment4/blob/diagram/airflow_pipeline.png)



## Project Goals

### Airflow Pipeline
1. Streamlined the process of parsing and extracting contents from documents, including text, tables, images, and graphs using Docling
2. Stored the parsed document vectors in Pinecone by generating OpenAI vector embeddings of document contents
3. Automated the data ingestion process and vector storage with Airflow

### Research Agent
1. Create a multi-agent system using Langraph to enhance document-based research and interactive query resolution.
2. Implemented multi-agent workflow with various agents, including:
- Document Selection Agent: Enable users to select and explore only processed documents.
- Arxiv Agent: Retrieve related academic research papers.
- Web Search Agent: Fetch supplementary data from the internet for broader context.
- RAG (Retrieval-Augmented Generation) Agent: Enable Q/A functionality by combining Pinecone-stored embeddings and LLM capabilities.
- LLM Integration: OpenAI API for generating context-aware responses to queries.

### FastAPI
1. Acts as the backend service to integrate Pinecone, Langraph agents, and the user interface.
2. Provide endpoints for document exploration, querying, and research interaction.

### Coagents
1. Provide a user-friendly interface for document exploration, querying, and interactive research sessions.
2. Allow users to ask detailed questions, generate reports, and interact with selected documents with multi-agent workflow.
3. Generated reports containing user queries, responses, images, and graphs are exportable in PDF and Codelabs formats.
4. A seamless user experience that integrates multiple agents and backend functionalities.
ce that integrates multiple agents and backend functionalities.

## Data Source
1. CFA Institute Research Foundation Publications: https://rpc.cfainstitute.org/en/research-foundation/publications#sort=%40officialz32xdate%20descending&f:SeriesContent=%5BResearch%20Foundation%5D

## Amazon S3 Link
- s3://publications-info/{document_id}


## Technologies
[![Docling](https://img.shields.io/badge/Docling-00B5B8?style=for-the-badge&logo=docling&logoColor=white)](https://docling.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-1A1A1A?style=for-the-badge&logo=pinecone&logoColor=white)](https://www.pinecone.io/)
[![Airflow](https://img.shields.io/badge/Airflow-17B3A8?style=for-the-badge&logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)
[![Amazon S3](https://img.shields.io/badge/Amazon%20S3-569A31?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/s3/)
[![Snowflake](https://img.shields.io/badge/Snowflake-29B1E5?style=for-the-badge&logo=snowflake&logoColor=white)](https://www.snowflake.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-000000?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![Arxiv Agent](https://img.shields.io/badge/Arxiv%20Agent-FF3C00?style=for-the-badge&logo=arxiv&logoColor=white)](https://arxiv.org/)
[![Web Search Agent](https://img.shields.io/badge/Web%20Search%20Agent-00A4E4?style=for-the-badge&logo=google&logoColor=white)](https://www.google.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-4C9E00?style=for-the-badge&logo=python&logoColor=white)](https://www.langgraph.com/)
[![CoAgent](https://img.shields.io/badge/CoAgent-007BFF?style=for-the-badge&logo=python&logoColor=white)](https://www.coagent.com/)
[![CLaaT](https://img.shields.io/badge/CLaaT-FF5722?style=for-the-badge&logo=python&logoColor=white)](https://codelabs.developers.google.com/)

## Prerequisites
Software Installations required for the project
1. Python Environment
A Python environment allows you to create isolated spaces for your Python projects, managing dependencies and versions separately

2. Poetry Environment/ Python Virtual Environment
- Poetry is a dependency management tool that helps you manage your Python packages and projects efficiently where a user can install all the dependencies onto pyproject.toml file
- Python Virtual Environment helps you manage your Python packages efficiently where a user can include all the dependencies in requirements.txt file

4. Packages
```bash
pip install -r requirements.txt
```

4. Visual Studio Code
An integrated development environment (IDE) that provides tools and features for coding, debugging, and version control.

5. Docker
 Docker allows you to package applications and their dependencies into containers, ensuring consistent environments across different platforms. All the dependencies will be installed on docker-compose.yaml file with env file

6. Amazon S3 Bucket
Amazon S3 (Simple Storage Service) is a cloud storage solution from AWS used to store files and objects. It provides scalable, secure, and cost-effective storage for all extracted publication files, including images, PDFs, and JSON data, organized under unique document IDs. This bucket serves as the primary cloud storage for file data accessible by the application.

8. Coagents
Coagents is an advanced framework designed for building interactive, agent-driven applications. It enables the integration of multiple AI agents working collaboratively to provide dynamic, context-aware user experiences. With Coagents, developers can create conversational interfaces and workflows tailored for complex research and analysis tasks, leveraging the power of multi-agent systems for seamless interaction.

9. Snowflake Database
Snowflake is a cloud-based data warehousing and analytics service that supports structured data storage. This project uses Snowflake to store extracted textual data, such as titles, summaries, cover image URLs, and PDF URLs from CFA publications. Snowflake also hosts user data and stores responses to user queries, enabling efficient querying and data retrieval.

10. Pinecone Vector Database
Pinecone is a cloud-native vector database used for storing embeddings of parsed document content, such as text chunks, tables, images, and graphs, in your research tool. It enables efficient similarity search by comparing user query embeddings with stored document embeddings using cosine similarity.

11. LangGraph Multi-Agent Framework
LangGraph is a powerful multi-agent framework designed to enhance document-based research and interactive query resolution by enabling seamless integration of multiple AI agents. This system facilitates intelligent and context-aware user interactions for complex research tasks, leveraging the capabilities of agents that can autonomously collaborate and perform tasks in parallel.

12. Document Selection Agent
This agent allows users to select and explore only processed documents, filtering out irrelevant or unprocessed content. This ensures users focus on the most relevant data for their research.

13. Arxiv Agent
This agent retrieves related academic research papers from ArXiv, enabling users to stay updated on the latest relevant literature and augment their research with additional references.

14. Web Search Agent
This agent fetches supplementary data from the web, providing a broader context for research tasks by retrieving external information that may not be available in the internal dataset.

15. RAG (Retrieval-Augmented Generation) Agent
The RAG agent combines embeddings from Pinecone-stored documents with the capabilities of language models to perform Q&A functionality. This agent enables efficient response generation by using document embeddings in combination with the knowledge available in the model.

16. LLM Integration
The OpenAI API is used to integrate large language models (LLMs) to generate context-aware responses to user queries. The LLM is able to interpret complex queries, summarize documents, and provide insightful answers based on the information retrieved by the various agents.


## Project Structure
```
Assignment3/
├── airflow
│   ├── Dockerfile
│   ├── POC
│   │   ├── MultiModalRAG.ipynb
│   │   ├── Stage1.ipynb
│   │   ├── Stage2.ipynb
│   │   ├── Stage3.py
│   │   └── stage1.csv
│   ├── chromedriver
│   │   ├── LICENSE.chromedriver
│   │   ├── THIRD_PARTY_NOTICES.chromedriver
│   │   └── chromedriver.exe
│   ├── dags
│   │   └── airflow_pipeline.py
│   ├── docker-compose.yaml
│   ├── rag_pipeline.py
│   ├── requirements.txt
│   ├── scraper.py
│   ├── snowflakeDB.py
│   ├── upload_to_S3.py
│   └── webscrape.py
├── diagram
│   ├── AirflowPipeline.py
│   ├── airflow_pipeline.png
│   ├── core_app_architecture.py
│   ├── core_application_pipeline.png
│   └── images
│       ├── Chroma.png
│       ├── Download.png
│       ├── InMemoryStore.png
│       ├── Langchain.png
│       ├── MultiVectorRetriever.png
│       ├── Nvidia-Logo.png
│       ├── Nvidia.png
│       ├── OpenAI.png
│       ├── PDF_documents.png
│       ├── PNG.png
│       ├── Question.png
│       ├── Snowflake.png
│       ├── Streamlit.png
│       ├── Text.png
│       ├── Unstructured.png
│       ├── cfa-institute.png
│       └── cleanlabs.png
├── docker-compose.yml
├── fastapi
│   ├── Dockerfile
│   ├── connectDB.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── routers.py
│   └── services.py
└── streamlit
    ├── Dockerfile
    ├── app.py
    ├── documentexplorer.py
    ├── homepage.py
    ├── loginpage.py
    ├── overview.py
    ├── qainterface.py
    ├── registerpage.py
    ├── requirements.txt
    └── summary.py

```

## How to run the application locally
1. **Clone the Repository**: Clone the repository onto your local machine and navigate to the directory within your terminal.

   ```bash
   git clone https://github.com/BigDataIA-Fall2024-TeamB6/Assignment4
   ```

2. **Install Docker**: Install docker and `docker compose` to run the application:

   - For Windows, Mac OS, simply download and install Docker Desktop from the official website to install docker and `docker compose` 
   [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)

   - For Linux (Ubuntu based distributions), 
   ```bash
   # Add Docker's official GPG key:
   sudo apt-get update
   sudo apt-get install ca-certificates curl
   sudo install -m 0755 -d /etc/apt/keyrings
   sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
   sudo chmod a+r /etc/apt/keyrings/docker.asc

   # Add the repository to Apt sources:
   echo \
   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
   $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt-get update 

   # Install packages for Docker
   sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

   # Check to see if docker is running 
   sudo docker run hello-world

3. **Run the application:** In the terminal within the directory, run 
   ```bash
   docker-compose up

   # To run with logging disabled, 
   docker-compose up -d

4. In the browser, 
   - visit `localhost:3000` to view the CoAgent application
   - visit `localhost:8000/docs` to view the FastAPI endpoint docs
   - visit `localhost:9000/` to view Codelabs document
