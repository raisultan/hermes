from pymilvus import Collection

from hermes.crawler.logger import logger
from hermes.extract import pdf_extract
from hermes.embed import get_len_safe_embeddings
from hermes.vector_db import prepare_record, insert
from hermes.normalize import normalize


def insert_pdf_to_db(collection: Collection, path: str) -> None:
    """Extracts text from PDF, normalizes it, embeds it, and inserts it into the database."""
    pages = pdf_extract(path)

    records = []
    for page in pages:
        normalized = normalize(page.content)
        embeddings = get_len_safe_embeddings(normalized)
        for embedding in embeddings:
            record = prepare_record(path, page.num, normalized, embedding)
            records.append(record)

    insert(collection, records)


def insert_pdfs_to_db(collection, pdf_files: list[str]) -> None:
    """Inserts PDFs to the database."""

    for num, pdf_file in enumerate(pdf_files, start=1):
        logger.info(f'{num} -- Inserting {pdf_file} to db...')
        try:
            insert_pdf_to_db(collection, pdf_file)
        except Exception as e:
            logger.error(f'{num} -- Failed to insert {pdf_file} to db: {repr(e)}\n')
        else:
            logger.info(f'{num} -- Inserted {pdf_file} to db!\n')
