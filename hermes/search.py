from pydantic import BaseModel
from pymilvus import Collection

from hermes.collection import CollectionConfig


class SearchResult(BaseModel):
    path: str
    page: int
    text: str
    distance: float


def search(collection: Collection, coll_cfg: CollectionConfig, embedding: list[float]) -> list[SearchResult]:
    """Search for the nearest neighbors of the given embedding."""
    collection.load()
    search_params = {'metric_type': coll_cfg.metric_type, 'params': coll_cfg.params}
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
