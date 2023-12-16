from pydantic import BaseModel


class SearchRequest(BaseModel):
    text: str
