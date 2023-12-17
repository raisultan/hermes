from fastapi import FastAPI, Depends
from pymilvus import Collection

from hermes.collection import INDEX_CONFIG
from hermes.embed import get_embedding
from hermes.search import SearchResult, search
from hermes.web.setup import get_collection
from hermes.web.schemas import SearchRequest

app = FastAPI()


@app.post('/api/search')
def search_handler(
    req: SearchRequest,
    collection: Collection = Depends(get_collection),
) -> list[SearchResult]:
    embedding = get_embedding(req.text)
    results = search(collection, INDEX_CONFIG, embedding)
    return results
