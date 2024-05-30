from typing import List, Dict

from fastapi import Query
from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    id: str
    text: str


class SearchRequest(BaseModel):
    text: str


class SaveDataRequest(BaseModel):
    encoding_model: str = Query('gigachat', enum=('gigachat', 'local_all_12', 'openai'))
    documents: List[str]
    metadatas: List[Dict]
