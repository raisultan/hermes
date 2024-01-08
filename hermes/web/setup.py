from pymilvus import Collection

from hermes.collection import connect_milvus, disconnect_milvus
from hermes.storage import connect_to_db, disconnect_from_db
from hermes.web.logger import logger


def get_milvus_connection() -> Collection:
    logger.info('Connecting to Milvus...')
    connect_milvus()
    yield
    logger.info('Disconnecting from Milvus...')
    disconnect_milvus()


def get_db_connection():
    logger.info('Connecting to db...')
    conn = connect_to_db()
    yield conn
    logger.info('Disconnecting from db...')
    disconnect_from_db(conn)
