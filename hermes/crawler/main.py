import uuid
from datetime import datetime

from rocketry import Rocketry
from rocketry.conds import every
from rocketry.args import CliArg

from hermes.find import pdf_find
from hermes.crawler.insert_pdfs_to_db import insert_pdfs_to_db
from hermes.crawler.create_collection import create_collection
from hermes.collection import connect_milvus, disconnect_milvus

app = Rocketry()
cli_dir_path = CliArg('--path')


@app.task(every('5 seconds'))
def create_find_extract_embed_insert(dir_path=cli_dir_path):
    """Creates collection, finds pdfs, extracts text, embeds and inserts into db."""
    pdf_files = pdf_find(dir_path)

    connect_milvus()

    collection_name = datetime.now().strftime("docs_%Y_%m_%d_%H_%M_%S")
    collection = create_collection(collection_name)
    insert_pdfs_to_db(collection, pdf_files)

    disconnect_milvus()


if __name__ == '__main__':
    app.run()
