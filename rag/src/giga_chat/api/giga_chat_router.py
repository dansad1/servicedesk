from fastapi import APIRouter, HTTPException
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document

from giga_chat.domain.gigachat_utils import simple_prompt, ru_en_translation, en_ru_translation, questions_to_text
from giga_chat.domain.llm import giga_chat_llm

giga_chat_router = APIRouter(
    prefix="/giga_chat",
    tags=["Giga Chat"],
)


@giga_chat_router.get(
    "/simple_prompt",
    response_model_exclude_none=True,
)
async def get_simple_prompt(
        message: str
):
    res = await simple_prompt(message)
    return res


@giga_chat_router.get(
    "/ru_en_translation",
    response_model_exclude_none=True,
)
async def get_ru_en_translation(
        message: str
):
    res = await ru_en_translation(message)
    return res



@giga_chat_router.get(
    "/en_ru_translation",
    response_model_exclude_none=True,
)
async def get_en_ru_translation(
        message: str
):
    res = await en_ru_translation(message)
    return res



@giga_chat_router.get(
    "/questions_to_text",
    response_model_exclude_none=True,
)
async def get_questions_to_text(
        message: str
):
    res = await questions_to_text(message)
    return res

