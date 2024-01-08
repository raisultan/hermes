from datetime import datetime

from rocketry import Rocketry
from rocketry.conds import every
from rocketry.args import CliArg

from hermes.collection import connect_milvus, create_collection, disconnect_milvus
from hermes.crawler.logger import logger
from hermes.crawler.insert_pdfs_to_db import insert_pdfs_to_db
from hermes.find import pdf_find
from hermes.storage import connect_to_db, write_collection_name, disconnect_from_db

app = Rocketry()
cli_dir_path = CliArg('--path')
db_conn = None


@app.task(on_startup=True)
def on_startup():
    global db_conn
    db_conn = connect_to_db()
    connect_milvus()


@app.task(on_shutdown=True)
def on_shutdown():
    global db_conn
    if db_conn:
        disconnect_from_db(db_conn)
    disconnect_milvus()


@app.task(every('5 seconds'))
def create_find_extract_embed_insert(dir_path: str = cli_dir_path):
    """Creates collection, finds pdfs, extracts text, embeds and inserts into db."""
    pdf_files = pdf_find(dir_path)
    logger.info(f'Found {pdf_files} pdf files in {dir_path}.')

    collection_name = datetime.now().strftime("docs_%Y_%m_%d_%H_%M_%S")

    logger.info(f'Creating collection {collection_name}...')
    collection = create_collection(collection_name)

    logger.info(f'Inserting pdf files to vector db...')
    insert_pdfs_to_db(collection, pdf_files)
    logger.info('Writing collection name to db...')
    write_collection_name(db_conn, collection_name)


if __name__ == '__main__':
    app.run()
