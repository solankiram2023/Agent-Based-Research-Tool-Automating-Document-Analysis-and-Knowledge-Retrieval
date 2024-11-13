import os
import boto3
import logging
from dotenv import load_dotenv

# Logger function
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load Environment variables
load_dotenv()

def download_files_from_s3(bucket_name, document_id):
    s3_client = boto3.client(
        's3',
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    local_folder_path = os.path.join(os.getcwd(), os.getenv("DOWNLOAD_DIRECTORY"))
    
    if not os.path.exists(local_folder_path):
        logger.info(f"Creating local directory to store files in {document_id}")
        os.makedirs(local_folder_path)
    else:
        logger.info(f"Local directory for document {document_id} already exists, skipping download ")

    try:
        # List all objects in the folder
        files = s3_client.list_objects_v2(Bucket = bucket_name, Prefix = document_id)
        if 'Contents' in files:
            for file in files['Contents']:
                file_key = file['Key']
                local_file_path = os.path.join(local_folder_path, file_key)
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                s3_client.download_file(bucket_name, file_key, local_file_path)
            logger.info(f"Downloaded all files from {document_id} successfully to {local_folder_path}")
        else:
            logger.info(f"No files found in folder {document_id}")


    except Exception as e:
        logger.info(f"Error downloading file: {e}")

def main():
    # Load environment variables
    bucket_name = os.getenv("S3_BUCKET_NAME")
    document_ids = ['68db7e4f057f494fb5b939ba258cefcd/', '97b6383e18bb48d1b7daceb27ad0a198/']

    for document_id in document_ids:
        download_files_from_s3(bucket_name, document_id)
        
if __name__ == '__main__':
    main()