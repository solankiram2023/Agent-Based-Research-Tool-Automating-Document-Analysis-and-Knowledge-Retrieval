import os 
import time
import logging
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc import PictureItem, TableItem
from docling.document_converter import DocumentConverter, PdfFormatOption

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def document_Parser(input_doc_path, output_dir):
    logging.info("Airflow - docParser.py - Parsing through PDF file")
    # Parameters for pipeline
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.images_scale = 5.0
    pipeline_options.generate_table_images = True
    pipeline_options.generate_picture_images = True
    logging.info("Airflow - docParser.py - All parameters set for the pipeline options")

    # Initializing document converter
    doc_converter = DocumentConverter(
        format_options = {
            InputFormat.PDF: PdfFormatOption(pipeline_options = pipeline_options)
        }
    )
    logging.info("Airflow - docParser.py - Document converter initialized")

    # Store the result
    conv_result = doc_converter.convert(input_doc_path)
    
    # Store results in local directory
    doc_filename = conv_result.input.file.stem

    tables_ouput_dir = Path(os.path.join(output_dir, "tables"))
    tables_ouput_dir.mkdir(parents=True, exist_ok=True)

    images_output_dir = Path(os.path.join(output_dir, "images"))
    images_output_dir.mkdir(parents=True, exist_ok=True)

    csv_files_output_dir = Path(os.path.join(output_dir, "csv_files"))
    csv_files_output_dir.mkdir(parents=True, exist_ok=True)

    # Save images and tables in respective folder
    table_counter = 0
    image_counter = 0

    for element, _level in conv_result.document.iterate_items():
        # Storing all the tables
        if isinstance(element, TableItem):
            table_counter += 1
            table_filename =  Path(os.path.join( tables_ouput_dir, f"table-{table_counter}.png"))
            with table_filename.open("wb") as fp:
                element.image.pil_image.save(fp, "PNG")
        
        # Storing images
        if isinstance(element, PictureItem):
            image_counter += 1
            image_filename = Path(os.path.join(images_output_dir, f"picture-{image_counter}.png"))
            with image_filename.open("wb") as fp:
                element.image.pil_image.save(fp, "PNG")
    
    logger.info(f"Airflow - docParser.py - All images and tables stored as PNG in images, tables folder")

    for table_ix, table in enumerate(conv_result.document.tables):
        table_df: pd.DataFrame = table.export_to_dataframe()
        csv_filename = Path(os.path.join(csv_files_output_dir, f"table-{table_ix+1}.csv"))
        table_df.to_csv(csv_filename)

    logger.info(f"Airflow - docParser.py - All tables stored in CSV format in csv_files folder")
    
    with (Path(os.path.join(output_dir, f"{doc_filename}.md"))).open("w", encoding = "utf-8") as fp:
        fp.write(conv_result.document.export_to_markdown())

    logger.info(f"Airflow - docParser.py - Text from PDF document is stored as markdown file")

def main():
    download_dir = Path(os.path.join(os.getcwd(), os.getenv("DOWNLOAD_DIRECTORY")))

    # Loop through all subdirectories (document_id folders) in the DOWNLOAD_DIRECTORY
    for document_id_dir in download_dir.iterdir():
        if document_id_dir.is_dir():

            # Initialize fname variable as None
            fname = None

            # Check if there's a PDF file inside the document_id directory
            dir_contents = os.listdir(document_id_dir)
            for file in dir_contents:
                if file.endswith(".pdf"):
                    fname = file
                    break  # Stop after the first PDF file is found

            # If a PDF file is found, proceed; otherwise, handle the error
            if fname:
                output_dir = Path(os.path.join(document_id_dir, "parsed_documents"))
                output_dir.mkdir(parents=True, exist_ok=True)
                input_dir = Path(os.path.join(document_id_dir, fname))
                document_Parser(input_dir, output_dir)
            else:
                logger.info(f"No PDF file found in {document_id_dir}")
        else:
            logger.info(f"{document_id_dir} is not a directory.")


if __name__ == "__main__":  
    main()