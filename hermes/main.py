def insert_pdf_to_db(collection, path: str) -> None:
    from hermes.extract import pdf_extract
    from hermes.embed import get_len_safe_embeddings
    from hermes.insert import prepare_record, insert
    from hermes.normalize import normalize_pdf

    pages = pdf_extract(path)

    records = []
    for page in pages:
        normalized = normalize_pdf(page.content)
        embeddings = get_len_safe_embeddings(normalized)
        for embedding in embeddings:
            record = prepare_record(path, page.num, normalized, embedding)
            records.append(record)

    insert(collection, records)


def find_pdfs_and_insert_to_db(collection, dir: str) -> None:
    from hermes.find import pdf_find

    pdf_files = pdf_find(dir)
    print(f'Found {len(pdf_files)} pdf files: {pdf_files}\n')

    for num, pdf_file in enumerate(pdf_files, start=1):
        print(f'{num} -- Inserting {pdf_file} to db...')
        try:
            insert_pdf_to_db(collection, pdf_file)
        except Exception as e:
            print(f'{num} -- Failed to insert {pdf_file} to db: {e}\n')
        else:
            print(f'{num} -- Inserted {pdf_file} to db!\n')


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
    find_pdfs_and_insert_to_db(collection, './')
    collection.load()
    end_time = time.time()

    disconnect_milvus()
    print(f'Time elapsed: {end_time - start_time} seconds')
