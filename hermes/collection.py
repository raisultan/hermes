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


def disconnect_milvus():
    connections.disconnect("default")


@dataclass(frozen=True)
class IndexConfig:
    index_type: str
    metric_type: str
    params: dict


# https://milvus.io/docs/index.md#HNSW
INDEX_CONFIG = IndexConfig(
    index_type="HNSW",
    metric_type="COSINE",
    params={"M": 24, "efConstruction": 256},
)


def build_indexes(collection: Collection, idx_cfg: IndexConfig) -> None:
    index = {
        "index_type": idx_cfg.index_type,
        "metric_type": idx_cfg.metric_type,
        "params": idx_cfg.params,
    }
    collection.create_index("embedding", index)


def create_collection():
    connect_milvus()

    collection = Collection(
        name=collection_name,
        schema=schema,
    )
    build_indexes(collection, INDEX_CONFIG)
    collection.load()

    disconnect_milvus()


if __name__ == "__main__":
    create_collection()
    print("Collection created successfully!")
