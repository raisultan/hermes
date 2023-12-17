def insert_pdf_to_db(collection, path: str) -> None:
    from hermes.extract import pdf_extract
    from hermes.embed import get_len_safe_embeddings
    from hermes.insert import prepare_record, insert

    pages = pdf_extract(path)

    records = []
    for page in pages:
        embeddings = get_len_safe_embeddings(page.content)
        for embedding in embeddings:
            record = prepare_record(path, page.num, page.content, embedding)
            records.append(record)

    insert(collection, records)


if __name__ == '__main__':
    import time

    from pymilvus import Collection
    from collection import connect_milvus, disconnect_milvus, collection_name, schema

    connect_milvus()
    collection = Collection(
        name=collection_name,
        schema=schema,
    )

    start_time = time.time()
    insert_pdf_to_db(collection, './cem.pdf')
    collection.load()
    end_time = time.time()

    disconnect_milvus()
    print('Successfully inserted records from pdf!')
    print(f'Time elapsed: {end_time - start_time} seconds')
