from sqlite3 import Connection

from fastapi import FastAPI, Depends
from pymilvus import Collection

from hermes.collection import INDEX_CONFIG, schema
from hermes.embed import get_embedding
from hermes.search import SearchResult, search
from hermes.storage import read_collection_name
from hermes.web.setup import get_milvus_connection, get_db_connection
from hermes.web.schemas import SearchRequest
from hermes.normalize import normalize_pdf

app = FastAPI()


@app.post('/api/search')
def search_handler(
    req: SearchRequest,
    collection: Collection = Depends(get_milvus_connection),
    db_conn: Connection = Depends(get_db_connection),
) -> list[SearchResult]:
    collection_name = read_collection_name(db_conn)
    print(f'\n\ncollection name: {collection_name}\n\n')
    collection = Collection(
        name=collection_name,
        schema=schema,
    )
    normalized = normalize_pdf(req.text)
    embedding = get_embedding(normalized)
    results = search(collection, INDEX_CONFIG, embedding)
    return results
