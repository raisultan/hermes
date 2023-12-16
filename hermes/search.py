from pydantic import BaseModel
from pymilvus import Collection


class SearchResult(BaseModel):
    path: str
    page: int
    text: str
    distance: float


def search(collection: Collection, embedding: list[float]) -> list[SearchResult]:
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
            result.append(SearchResult(
                path=entity.get('path'),
                page=entity.get('page'),
                text=entity.get('text'),
                distance=hit.distance,
            ))
    return result
