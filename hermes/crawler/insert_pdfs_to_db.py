import asyncio

from pymilvus import Collection

from hermes.crawler.logger import logger
from hermes.extract import PDFPage, pdf_extract
from hermes.embed import get_len_safe_embeddings
from hermes.vector_db import prepare_record, insert
from hermes.normalize import normalize
from hermes.utils import async_track_time


async def process_one_page(page: PDFPage) -> list[dict]:
    normalized = normalize(page.content)
    embeddings = await get_len_safe_embeddings(normalized)
    return [prepare_record(page.path, page.num, normalized, embedding) for embedding in embeddings]


@async_track_time
async def process_pdf(path: str) -> list[dict]:
    """
    Extracts text from PDF, normalizes it, embeds it, and prepares records.
    This function is designed to run in a separate process.
    """
    records = []
    pages = pdf_extract(path)
    tasks = [process_one_page(page) for page in pages]
    results = await asyncio.gather(*tasks)

    for result in results:
        if isinstance(result, Exception):
            logger.error(f'Error processing {path}: {repr(result)}')
        else:
            records.extend(result)
    return records


@async_track_time
async def insert_pdf_to_db(collection: Collection, pdf_file: str):
    """
    Handles the process of extracting data from a PDF and inserting it into the database.
    """
    records = await process_pdf(pdf_file)
    if records:
        insert(collection, records)


@async_track_time
async def insert_pdfs_to_db(collection, pdf_files: list[str]):
    """
    Manages the insertion of multiple PDFs into the database.
    """
    logger.info(f'Inserting {len(pdf_files)} pdfs to db...')
    tasks = [insert_pdf_to_db(collection, pdf_file) for pdf_file in pdf_files]
    await asyncio.gather(*tasks)
