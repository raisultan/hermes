from hermes.extract import pdf_extract
from hermes.embed import get_len_safe_embeddings
from hermes.insert import prepare_record, insert


def load_pdf_to_db(collection, path: str):
    pages = pdf_extract(path)

    records = []
    for page in pages:
        embeddings = get_len_safe_embeddings(page.content)
        for embedding in embeddings:
            record = prepare_record(path, page.num, page.content, embedding)
            records.append(record)

    insert(collection, records)


def search(text: str):
    from pymilvus import Collection
    from collection import connect_milvus, disconnect_milvus, collection_name, schema

    from embed import get_embedding
    from search import search

    connect_milvus()
    collection = Collection(
        name=collection_name,
        schema=schema,
    )

    embedding = get_embedding(text)
    search_results = search(collection, embedding)

    disconnect_milvus()
    return search_results


if __name__ == '__main__':
    from pymilvus import Collection
    from collection import connect_milvus, disconnect_milvus, collection_name, schema
    connect_milvus()
    collection = Collection(
        name=collection_name,
        schema=schema,
    )
    load_pdf_to_db(collection, './cem.pdf')
    collection.load()
    disconnect_milvus()
    print('Successfully inserted records from pdf!')
