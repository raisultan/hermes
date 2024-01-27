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

def delete_by_paths(collection: Collection, paths: list[str]) -> None:
    collection.load()
    expr = f'path in [{", ".join(map(repr, paths))}]'
    collection.delete(expr)
    collection.flush()
