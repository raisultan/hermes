from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections

VECTOR_DIMENSIONS = 1536

path = FieldSchema(
  name="path",
  dtype=DataType.VARCHAR,
  is_primary=True,
  max_length=1024,
)
text = FieldSchema(
  name="text",
  dtype=DataType.VARCHAR,
  max_length=65_535,
)
embedding = FieldSchema(
  name="embedding",
  dtype=DataType.FLOAT_VECTOR,
  dim=VECTOR_DIMENSIONS,
)

schema = CollectionSchema(
  fields=[path, text, embedding],
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


def build_indexes(collection: Collection) -> None:
    index = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128},
    }
    collection.create_index("embedding", index)


def create_collection():
    connect_milvus()

    collection = Collection(
        name=collection_name,
        schema=schema,
    )
    build_indexes(collection)
    collection.load()

    disconnect_milvus()


if __name__ == "__main__":
    create_collection()
    print("Collection created successfully!")
