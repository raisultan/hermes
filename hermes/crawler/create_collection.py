
from hermes.collection import connect_milvus, build_indexes, disconnect_milvus, schema, INDEX_CONFIG

from pymilvus import Collection


def create_collection(name: str) -> Collection:
    collection = Collection(
        name=name,
        schema=schema,
    )
    build_indexes(collection, INDEX_CONFIG)
    collection.load()
    return collection
