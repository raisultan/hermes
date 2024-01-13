from datetime import datetime

from pymilvus import Collection
from rocketry import Rocketry
from rocketry.conds import every, daily
from rocketry.args import Task

from hermes.collection import connect_milvus, create_collection, disconnect_milvus, get_collection
from hermes.crawler.logger import logger
from hermes.crawler.insert_pdfs_to_db import insert_pdfs_to_db
from hermes.crawler.track_changes import track_changes
from hermes.find import pdf_find
from hermes.storage import (
    connect_to_db,
    read_dir_path,
    read_pdf_paths,
    read_collection_name,
    write_collection_name,
    write_pdf_paths,
    disconnect_from_db,
)
from hermes.vector_db import delete_by_paths

app = Rocketry()
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


@app.cond()
def done(task = Task()):
    return task.status != 'run'


def create_new_collection() -> Collection:
    collection_name = datetime.now().strftime("docs_%Y_%m_%d_%H_%M_%S")
    logger.info(f'Creating collection {collection_name}...')
    collection = create_collection(collection_name)

    logger.info('Writing collection name to db...')
    write_collection_name(db_conn, collection_name)
    return collection


@app.task(daily)
def compact_collection():
    """Compacts collection."""
    collection_name = read_collection_name(db_conn)
    collection = get_collection(collection_name)
    collection.load()
    collection.compact()


@app.task(done & every('1 minute'))
def create_find_extract_embed_insert():
    """Creates collection, finds pdfs, extracts text, embeds and inserts into db."""
    try:
        dir_path = read_dir_path(db_conn)
    except Exception as e:
        logger.error(f'Failed to read dir path from db: {repr(e)}.')
        return None
    if not dir_path:
        logger.info('No dir path found in db.')
        return None

    new_pdf_paths = pdf_find(dir_path)
    logger.info(f'Found {new_pdf_paths} pdf files in {dir_path}.')

    try:
        prev_pdf_paths = read_pdf_paths(db_conn)
    except Exception as e:
        logger.error(f'Failed to read pdf paths from db: {repr(e)}.')
        prev_pdf_paths = []

    changes = track_changes(prev_pdf_paths, new_pdf_paths)
    if not changes.is_changed:
        logger.info('No changes detected.')
        return None

    logger.info(f'Changes: {changes}.')
    try:
        collection_name = read_collection_name(db_conn)
        collection = get_collection(collection_name)
    except Exception as e:
        logger.error(f'Failed to load collection: {repr(e)}.')
        collection = create_new_collection()

    if changes.deleted:
        logger.info(f'Deleting {changes.deleted} from vector db...')
        delete_by_paths(collection, changes.deleted)

    if changes.added:
        logger.info(f'Adding {changes.added} to vector db...')
        insert_pdfs_to_db(collection, changes.added)

    logger.info(f'Writing pdf paths to db...')
    write_pdf_paths(db_conn, new_pdf_paths)


if __name__ == '__main__':
    app.run()
