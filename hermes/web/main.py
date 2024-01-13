from sqlite3 import Connection

from fastapi import FastAPI, Depends

from hermes.collection import INDEX_CONFIG, get_collection
from hermes.embed import get_embedding
from hermes.search import SearchResult, search
from hermes.storage import read_dir_path, read_collection_name, write_dir_path
from hermes.web.setup import get_milvus_connection, get_db_connection
from hermes.web.schemas import DirPathRequest, DirPathResponse, SearchRequest
from hermes.normalize import normalize

app = FastAPI()


@app.post('/api/search')
def search_handler(
    req: SearchRequest,
    _: None = Depends(get_milvus_connection),
    db_conn: Connection = Depends(get_db_connection),
) -> list[SearchResult]:
    collection_name = read_collection_name(db_conn)
    collection = get_collection(collection_name)

    normalized_txt = normalize(req.text)
    embedding = get_embedding(normalized_txt)
    results = search(collection, INDEX_CONFIG, embedding)
    return results


@app.post('/api/dir_path')
def search_handler(
    req: DirPathRequest,
    db_conn: Connection = Depends(get_db_connection),
) -> dict:
    write_dir_path(db_conn, req.dir_path)
    return {'status': 'ok'}


@app.get('/api/dir_path')
def search_handler(
    db_conn: Connection = Depends(get_db_connection),
) -> DirPathResponse:
    dir_path = read_dir_path(db_conn)
    return DirPathResponse(dir_path=dir_path)
