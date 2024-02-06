"""Module defines collection, index config and a function to create it."""

from dataclasses import dataclass

from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections

VECTOR_DIMENSIONS = 1536

path = FieldSchema(
  name="path",
  dtype=DataType.VARCHAR,
  is_primary=True,
  max_length=1024,
)
page = FieldSchema(
    name="page",
    dtype=DataType.INT16,
)
text = FieldSchema(
  name="text",
  dtype=DataType.VARCHAR,
  max_length=16_384,
)
embedding = FieldSchema(
  name="embedding",
  dtype=DataType.FLOAT_VECTOR,
  dim=VECTOR_DIMENSIONS,
)

schema = CollectionSchema(
  fields=[path, page, text, embedding],
  description="Documents",
)
collection_name = "docs"

def connect_milvus():
    connections.connect(
        alias="default",
        user='username',
        password='password',
        host='localhost',
        port='19530',
    )


def disconnect_milvus() -> None:
    connections.disconnect("default")


@dataclass(frozen=True)
class CollectionConfig:
    index_type: str
    metric_type: str
    params: dict


# https://milvus.io/docs/index.md#HNSW
INDEX_CONFIG = CollectionConfig(
    index_type="HNSW",
    metric_type="COSINE",
    params={"M": 24, "efConstruction": 256},
)


def build_indexes(collection: Collection, coll_cfg: CollectionConfig) -> None:
    index = {
        "index_type": coll_cfg.index_type,
        "metric_type": coll_cfg.metric_type,
        "params": coll_cfg.params,
    }
    collection.create_index("embedding", index)
    collection.flush()


def get_collection(collection_name: str) -> Collection:
    return Collection(name=collection_name)


def create_collection(name: str) -> Collection:
    collection = Collection(
        name=name,
        schema=schema,
    )
    build_indexes(collection, INDEX_CONFIG)
    return collection
