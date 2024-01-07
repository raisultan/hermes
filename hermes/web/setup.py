from pymilvus import Collection

from hermes.collection import connect_milvus, disconnect_milvus
from hermes.storage import connect_to_db, disconnect_from_db

def get_milvus_connection() -> Collection:
    connect_milvus()
    yield
    disconnect_milvus()


def get_db_connection():
    conn = connect_to_db()
    yield conn
    disconnect_from_db(conn)
