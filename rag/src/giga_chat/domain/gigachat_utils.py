from langchain_core.messages import SystemMessage, HumanMessage

from giga_chat.domain.llm import giga_chat_llm
from giga_chat.prompts.local_patent_prompts import ru_en_translation_prompt, en_ru_translation_prompt, \
    questions_to_text_prompt

SYSTEM_PROMPT = (
    "Ты — русскоязычный автоматический ассистент пользователя платформы отдела. Ты помогаешь людям находить точную информацию в тексте отчета. "
    "Отвечай на вопрос пользователя только на основе информации из отчета. Если отчет не содержит релевантной информации отвечай: не достаточно информации для ответа.  "
)

SYSTEM_PROMPT_EN = (
    "You are an automated assistant in the patent department. You help people find accurate information in the body of a report."
    "Answer the user's query only based on information from the report."
    " If the report fragment does not contain relevant information, answer: not enough information to answer."
                 )

MOODLE_SYSTEM_PROMPT = (
    "Ты — русскоязычный автоматический ассистент образовательных курсов. Ты помогаешь людям находить точную информацию в тексте отчета. "
    "Отвечай на вопрос пользователя только на основе информации из отчета."
)

async def simple_prompt(message: str):
    messages = [SystemMessage(content=message)]
    output = await giga_chat_llm.ainvoke(messages)
    return output.content


async def rag_prompt(query: str, context: str):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f'Report fragment:\n{context}\nQuestion:\n{query}')
    ]
    output = await giga_chat_llm.ainvoke(messages)
    return output.content


async def rag_prompt_with_patent_numbers(query: str, context: str):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f'Report fragment:\n{context}\nQuestion:\n{query}')
    ]
    output = await giga_chat_llm.ainvoke(messages)
    return output.content


async def moodle_rag_prompt(query: str, context: str):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f'Фрагмент отчета:\n{context}\nВопрос:\n{query}')
    ]
    output = await giga_chat_llm.ainvoke(messages)
    return output.content



async def ru_en_translation(message: str):
    prompt = ru_en_translation_prompt.format(text=message)
    messages = [
        SystemMessage(content=prompt)
    ]
    output = await giga_chat_llm.ainvoke(messages)
    return output.content


async def en_ru_translation(message: str):
    prompt = en_ru_translation_prompt.format(text=message)
    messages = [
        SystemMessage(content=prompt)
    ]
    output = await giga_chat_llm.ainvoke(messages)
    return output.content


async def questions_to_text(message: str):
    prompt = questions_to_text_prompt.format(text=message)
    messages = [
        SystemMessage(content=prompt)
    ]
    output = await giga_chat_llm.ainvoke(messages)
    return output.content



