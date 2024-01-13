from pydantic import BaseModel


class SearchRequest(BaseModel):
    text: str


class DirPathRequest(BaseModel):
    dir_path: str


class DirPathResponse(BaseModel):
    dir_path: str
