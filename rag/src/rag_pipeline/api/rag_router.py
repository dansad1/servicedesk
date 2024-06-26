from typing import List
from fastapi import APIRouter, Query

from embeddings.api.schema import SearchRequest
from rag_pipeline.domain.rag_utils import rag_db_response, fill_rag_db, rag_final_response

rag_router = APIRouter(
    prefix="/rag_router",
    tags=["rag"],
)


@rag_router.post(
    "/fill_db",
)
async def fill_db(encoding_model: str = Query('gigachat', enum=('gigachat', 'local_all_12', 'openai'))
):
    res = await fill_rag_db(encoding_model)
    return res


@rag_router.post(
    "/rag_db_response",
)
async def get_rag_db_response(
        request: SearchRequest,
        encoding_model: str = Query('gigachat', enum=('gigachat', 'local_all_12', 'openai')),
        n_results: int = Query(10),
        include_embeddings: bool = Query(False),
        ids: List[str] = Query([], alias="id"),
):
    res = await rag_db_response(request, encoding_model, n_results, include_embeddings, ids)
    return res


@rag_router.post(
    "/rag_final_response",
)
async def get_rag_final_response(
        request: SearchRequest,

        encoding_model: str = Query('gigachat', enum=('gigachat', 'local_all_12', 'openai')),
        n_results: int = Query(3),
        include_embeddings: bool = Query(False),
        ids: List[str] = Query([], alias="id"),
):
    res = await rag_final_response(request, encoding_model, n_results, include_embeddings, ids)
    return res


