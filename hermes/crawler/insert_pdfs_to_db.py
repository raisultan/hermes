import asyncio
import concurrent.futures

from pymilvus import Collection

from hermes.crawler.logger import logger
from hermes.extract import pdf_extract
from hermes.embed import get_len_safe_embeddings
from hermes.vector_db import prepare_record, insert
from hermes.normalize import normalize
from hermes.utils import async_track_time


def process_pdf(pdf_file: str):
    """
    Extracts text from PDF, normalizes it, embeds it, and prepares records.
    This function is designed to run in a separate process.
    """
    try:
        pages = pdf_extract(pdf_file)
        records = []
        for page in pages:
            normalized = normalize(page.content)
            embeddings = get_len_safe_embeddings(normalized)
            for embedding in embeddings:
                record = prepare_record(pdf_file, page.num, normalized, embedding)
                records.append(record)
        return records
    except Exception as e:
        logger.error(f'Error processing {pdf_file}: {e}')
        return []


async def insert_pdf_to_db(executor, collection: Collection, pdf_file: str):
    """
    Handles the process of extracting data from a PDF and inserting it into the database.
    """
    loop = asyncio.get_running_loop()
    records = await loop.run_in_executor(executor, process_pdf, pdf_file)
    if records:
        insert(collection, records)


@async_track_time
async def insert_pdfs_to_db(collection, pdf_files: list[str]):
    """
    Manages the insertion of multiple PDFs into the database.
    """
    logger.info(f'Inserting {len(pdf_files)} pdfs to db...')
    with concurrent.futures.ProcessPoolExecutor() as executor:
        tasks = [insert_pdf_to_db(executor, collection, pdf_file) for pdf_file in pdf_files]
        await asyncio.gather(*tasks)
