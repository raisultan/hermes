from pymilvus import Collection


def prepare_record(
    path: str,
    page_num: int,
    text: str,
    embedding: list[float],
) -> list:
    return {'path': path, 'page': page_num, 'text': text, 'embedding': embedding}


def insert(collection: Collection, records: list[dict]) -> None:
    collection.insert(records)
    collection.flush()
