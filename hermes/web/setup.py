from pymilvus import Collection

from hermes.collection import connect_milvus, disconnect_milvus, collection_name, schema

def get_collection() -> Collection:
    connect_milvus()
    collection = Collection(
        name=collection_name,
        schema=schema,
    )

    try:
        yield collection
    finally:
        disconnect_milvus()
