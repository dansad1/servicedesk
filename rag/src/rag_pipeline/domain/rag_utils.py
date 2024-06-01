import asyncio
import os
from typing import List

from fastapi import Query
from langchain_text_splitters import split_text_on_tokens

from embeddings.api.schema import SearchRequest, SaveDataRequest
from embeddings.domain.chroma_utils import search, add_vectors_to_db
from file_processing.file_readers.readers import read_xlsx, read_docx
from file_processing.text_cleaners.cleaning import en_embedding_clean
from file_processing.text_splitters.ru_token_splitter import RU_TOKEN_SPLITTER
from giga_chat.domain.gigachat_utils import rag_prompt, ru_en_translation, en_ru_translation


async def rag_db_response(request: SearchRequest,
                          encoding_model: str = Query('gigachat', enum=('gigachat', 'local_all_12', 'openai')),
                          n_results: int = Query(10),
                          include_embeddings: bool = Query(False),
                          ids: List[str] = Query([], alias="id"), ):
    request.text = await ru_en_translation(request.text)
    results = await search(request, encoding_model, n_results, include_embeddings, ids)

    tasks = [en_ru_translation(r) for r in results['documents'][0]]
    ru_res = await asyncio.gather(*tasks)
    return results, ru_res


async def rag_final_response(request: SearchRequest,
                             encoding_model: str = Query('gigachat', enum=('gigachat', 'local_all_12', 'openai')),
                             n_results: int = Query(10),
                             include_embeddings: bool = Query(False),
                             ids: List[str] = Query([], alias="id"), ):
    results = await search(request, encoding_model, n_results, include_embeddings, ids)
    if not results:
        return "data base is empty", ''
    context = '\n'.join(results['documents'][0])

    output = await rag_prompt(request.text, context)

    return output, context


async def compose_SaveDatasetRequest(file_path, encoding_model):
    items = read_docx(file_path)
    docs = []
    metadatas = []
    text_spliter = RU_TOKEN_SPLITTER(tokens_per_chunk=200, chunk_overlap=40)

    text = items
    meta = {'file_path': file_path}
    chunks = split_text_on_tokens(text=text, tokenizer=text_spliter)
    docs += chunks
    metadatas += [meta.copy() for _ in chunks]
    return SaveDataRequest(encoding_model=encoding_model, documents=docs, metadatas=metadatas)


async def fill_rag_db_old(encoding_model: str = Query('gigachat', enum=('gigachat', 'local_all_12', 'openai'))):
    file_path: str = '/opt/app-root/rag/not_included_data/инструкция.docx'
    request = await compose_SaveDatasetRequest(file_path, encoding_model)
    await add_vectors_to_db(request)


async def fill_rag_db(encoding_model: str = Query('gigachat', enum=('gigachat', 'local_all_12', 'openai'))):
    directory: str = '/opt/app-root/rag/not_included_data'
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if filename.endswith('docx'):
            request = await compose_SaveDatasetRequest(file_path, encoding_model)
            await add_vectors_to_db(request)
        os.remove(file_path)
