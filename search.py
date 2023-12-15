from pymilvus import Collection

from embed import get_embedding


def search(collection: Collection, text: str) -> list[dict]:
    collection.load()
    embedding = get_embedding(text)
    search_params = {'metric_type': 'L2', 'params': {'nprobe': 10}}
    raw_result = collection.search(
        [embedding],
        'embedding',
        search_params,
        limit=5,
        output_fields=['path', 'text'],
    )
    result = []
    for hits in raw_result:
        for hit in hits:
            entity = hit.entity
            result.append({
                'path': entity.get('path'),
                'text': entity.get('text'),
                'distance': hit.distance,
            })
    return result
