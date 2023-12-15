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


def search(collection: Collection, embedding: list[float]) -> list[dict]:
    collection.load()
    search_params = {'metric_type': 'L2', 'params': {'nprobe': 10}}
    raw_result = collection.search(
        [embedding],
        'embedding',
        search_params,
        limit=5,
        output_fields=['path', 'page', 'text'],
    )
    result = []
    for hits in raw_result:
        for hit in hits:
            entity = hit.entity
            result.append({
                'path': entity.get('path'),
                'page': entity.get('page'),
                'text': entity.get('text'),
                'distance': hit.distance,
            })
    return result
