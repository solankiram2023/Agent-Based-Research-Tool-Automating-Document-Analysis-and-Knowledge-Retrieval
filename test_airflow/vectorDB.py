import os 
import math
import uuid
import time
import base64
import openai
import logging
import pinecone
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv
from pinecone import ServerlessSpec
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain.schema import HumanMessage

load_dotenv()

# Initialize logger
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

def encode_image_to_base64(image_path):
    try:
        with open(image_path, 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        print(f"Error encoding image to base64: {e}")
        return None
    
def summarize_image_with_gpt(image_base64):
    try:
        prompt = f"You are an assistant tasked with summarizing image {image_base64} for retrieval via RAGs. These summaries will be embedded and used to retrieve the raw image via RAGs. Give a concise summary of the image that is well optimized for retrieval via RAGs."

        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Generate response from GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5  # Adjust as needed for consistency
        )

        summary = response['choices'][0]['message']['content'].strip()
        return summary
    except Exception as e:
        print(f"Error generating summary with GPT-4o: {e}")
        return None
    
def image_summarize(img_base64, prompt):
    chat = ChatOpenAI(
        model       = "gpt-4o", 
        max_tokens  = 1024,
        api_key     = os.getenv("OPEN_AI_API")
    )

    msg = chat.invoke(
        [
            HumanMessage(
                content=[
                    {
                        "type": "text", 
                        "text": prompt
                    },
                    {
                        "type"      : "image_url",
                        "image_url" : {"url": f"data:image/jpeg;base64,{img_base64}"},
                    },
                ]
            )
        ]
    )
    return msg.content


def process_images_and_tables(folder_path):
    summaries = []

    prompt = f"You are an assistant tasked with summarizing images for retrieval via RAGs. These summaries will be embedded and used to retrieve the raw image via RAGs. Give a concise summary of the image that is well optimized for retrieval via RAGs."


    for image_filename in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_filename)

        if os.path.isfile(image_path):
            print(f"Processing image {image_filename}")

            # Encode image to base64
            image_base64 = encode_image_to_base64(image_path)
            if image_base64:
                image_summary = image_summarize(image_base64, prompt)
                print(f"image {image_filename} and summary = {image_summary}")
                if image_summary:
                    summaries.append(image_summary)
                    summary_filename = os.path.splitext(image_filename)[0] + "_summary.txt"
                    summary_filedir = Path(os.path.join(folder_path, "summaries"))
                    summary_filedir.mkdir(parents=True, exist_ok=True)
                    summary_filepath = os.path.join(summary_filedir, summary_filename)
                    with open(summary_filepath, "w") as file:
                        file.write(image_summary)
                else:
                    summaries.append(f"Failed to summarize image: {image_filename}")
            else:
                summaries.append(f"Failed to encode image: {image_filename}")

    return summaries




def create_embeddings_in_batches(embedding_model, texts, batch_size = 5):
    all_embeddings = []
    total_batches = math.ceil(len(texts)/ batch_size)

    for i in range(total_batches):
        # Get the start and end indices for the current batch
        batch_texts = texts[i * batch_size: (i+1) * batch_size]
        
        # Generate embeddings for the current branch
        batch_embeddings = embedding_model.embed_documents(batch_texts)

        # Append the embeddings to the list of all embeddings
        all_embeddings.extend(batch_embeddings)

        print(f"Processed batch {i+1}/{total_batches} with {len(batch_texts)} texts.")

    return all_embeddings

def main():
    markdown_file_path = "/Users/deepthi/Documents/Courses/bigdata/Assignment4/test_airflow/downloads/68db7e4f057f494fb5b939ba258cefcd/parsed_documents/Revisiting-the-Equity-Risk-Premium.md"
    images_folder_path = "/Users/deepthi/Documents/Courses/bigdata/Assignment4/test_airflow/downloads/68db7e4f057f494fb5b939ba258cefcd/parsed_documents/images"
    tables_folder_path = "/Users/deepthi/Documents/Courses/bigdata/Assignment4/test_airflow/downloads/68db7e4f057f494fb5b939ba258cefcd/parsed_documents/tables"

    



    # Load data from markdown file using Unstructured
    loader = UnstructuredMarkdownLoader(markdown_file_path, mode = "elements")
    data = loader.load()

    # Text splitter for splitting data into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 4000,
        chunk_overlap = 200
    )

    chunks = []
    # Process markdown text
    for element in data:
        text = element.page_content
        chunks.extend(text_splitter.create_documents([text]))
    
    image_summaries = process_images_and_tables(images_folder_path)
    table_summaries = process_images_and_tables(tables_folder_path)

    # Prepare text data for embedding (extract the actual text from chunks)
    texts = [chunk.page_content for chunk in chunks] + image_summaries + table_summaries

    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large", api_key=os.getenv("OPENAI_API_KEY"))

    embeddings = create_embeddings_in_batches(embedding_model, texts)

    # Print the length of embeddings and the size of the first embedding vector
    print(f"Total embeddings generated: {len(embeddings)}")
    print(f"Size of first embedding: {len(embeddings[0])}")


    # Initialize Pinecone client
    pc = pinecone.Pinecone(api_key = os.getenv("PINECONE_API_KEY"))

    # Pinecone index name
    index_name = 'langchain-document-index'

    # Check if the index exists, delete if present, then create a new one
    if index_name in pc.list_indexes().names():
        pc.delete_index(index_name)
        print(f"Deleted existing index {index_name}.")

    # Create a spec for the index
    spec = ServerlessSpec(cloud="aws", region="us-east-1")

    pc.create_index(
        name=index_name,
        dimension=3072,
        metric='cosine',
        spec=spec
    )
    print(f"Created new index {index_name}.")

    # Wait for index to be initialized
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)

    # Connect to the index
    index = pc.Index(index_name)

    time.sleep(1)
    # view index stats
    index.describe_index_stats()

    # Create unique IDs for each document
    ids = [str(uuid.uuid4()) for _ in range(len(texts))]  # Use consistent IDs if overwriting is needed

    # Convert text data into Langchain Document objects
    docs = [Document(page_content=texts[i], metadata={"id": ids[i]}) for i in range(len(texts))]
    
    docsearch = PineconeVectorStore.from_documents(docs, embedding_model, index_name=index_name)
    print(f"Upserted vectors into Pinecone using PineconeVectorStore.")


if __name__ == '__main__':
    main()