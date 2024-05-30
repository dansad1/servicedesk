# -*- coding: utf-8 -*-
from pathlib import Path
from collections import defaultdict
import pandas as pd
import os
from dotenv import load_dotenv
import logging

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

from pydantic import Field
from typing import Any, List, Optional, Union

from giga_chat.local.config import giga_chat_api_config

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger()

load_dotenv()
GIGACHAT_CREDENTIALS = os.getenv('GIGACHAT_CREDENTIALS')

SYSTEM_PROMPT = (
    "Ты — русскоязычный автоматический ассистент патентного отдела. Ты помогаешь людям находить точную информацию в тексте отчета. "
    "Отвечай на вопрос пользователя только на основе информации из отчета. Если фрагмент отчета не содержит "
    "релевантной информации, отвечай: не достаточно информации для ответа."
)

NEUTRAL_SYSTEM_PROMPT = ("Ты — русскоязычный автоматический ассистент геолога.")


class GigaChatLLM(LLM):
    model_name: str = Field('GigaChat', alias='model_name')
    """The name of the model to use."""

    tokenizer_name: str = Field('GigaChat', alias='tokenizer_name')
    """The name of the sentence tokenizer to use."""

    config: Any = None  #: :meta private:
    """The reference to the loaded configuration."""

    tokenizer: Any = None  #: :meta private:
    """The reference to the loaded tokenizer."""

    model: Any = None  #: :meta private:
    """The reference to the loaded model."""

    accelerator: Any = None  #: :meta private:
    """The reference to the loaded hf device accelerator."""

    attn_impl: str = Field("torch", alias='attn_impl')
    """The attention implementation to use."""

    # torch_dtype: Any = Field(torch.float16, alias='torch_dtype')
    """The torch data type to use."""

    max_new_tokens: Optional[int] = Field(1024, alias='max_new_tokens')
    """The maximum number of tokens to generate."""

    do_sample: Optional[bool] = Field(True, alias='do_sample')
    """Whether to sample or not."""

    temperature: Optional[float] = Field(1e-10, alias='temperature')
    """The temperature to use for sampling."""

    echo: Optional[bool] = Field(False, alias='echo')
    """Whether to echo the prompt."""

    stop: Optional[List[str]] = []
    """A list of strings to stop generation when encountered."""

    memory: defaultdict = defaultdict(list)

    def __init__(self) -> None:
        super().__init__()
        self.model_name = 'GigaChat'
        self.tokenizer_name = 'GigaChat'
        self.model = None
        self.tokenizer = None
        self.config = None
        self.memory = defaultdict(list)
        self.init_llm()

    def init_llm(self) -> None:
        self.model = GigaChat(
            credentials=giga_chat_api_config.TOKEN,
            scope=giga_chat_api_config.SCOPE,
            verify_ssl_certs=False)
        self.model.temperature = 1e-10
        self.model.max_tokens = 1024
        logger.info(f'Initialized GigaChat model.')

    def response(self, query: str, context: str, true_answer: str = '', true_context: str = '', add_to_memory: bool = False ):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f'Фрагмент отчета:\n{context}\nВопрос:\n{query}')
        ]
        output = self.model(messages).content

        if add_to_memory:
            self.memory['question'].append(query)
            self.memory['context'].append(context)
            self.memory['expected context'].append(true_context)
            self.memory['answer'].append(output)
            self.memory['expected answer'].append(true_answer)
        return output

    def simple_response(self, message):
        messages = [SystemMessage(content=message)]
        output = self.model(messages).content
        return output

    def save_responses(self, dir_path: str):
        filename = str(Path(dir_path) / 'output.xlsx')
        responses = pd.DataFrame(self.memory)
        responses.to_excel(filename, index=False)
        logger.info(f'Saved model responses to {filename}')

    def clear_memory(self):
        self.memory = defaultdict(list)
        logger.info('Cleared memory.')

    @property
    def _llm_type(self) -> str:
        """Return the type of llm."""
        return 'GigaChat'

    def _call(self, input_data: Union[str, list],
              stop: list[str] = None,
              run_manager: CallbackManagerForLLMRun = None,
              **kwargs: Any) -> str:
        if isinstance(input_data, str):
            input_data = [
                SystemMessage(content=NEUTRAL_SYSTEM_PROMPT),
                HumanMessage(content=input_data)
            ]
        output = self.model(input_data).content
        return output


if __name__ == '__main__':
    rag_llm = GigaChatLLM()
    query = 'о чем данный текст?'
    context = 'The invention discloses a lithium battery formation method which comprises the following steps: 1, soaking a cell tab upwards in an electrolyte tank filled with electrolyte and enabling the range that a cell main body is immersed in the electrolyte not to exceed four fifths of the height of a cell; 2, clamping and preheating the cell under a clamping pressure of 0.05 MPa to 0.6 MPa; 3, continuously soaking the clamped and preheated cell in the electrolyte tank, sealing and vacuumizing the electrolyte tank and carrying out pre-charging; 4, applying a force of 0.2 MPa to 1 MPa to both sides of the pre-charged cell to clamp the cell and packaging the cell. A lithium battery obtained by adopting the lithium battery formation method disclosed by the invention has no black spots and separated lithium and is excellent in interface; capacity of the lithium battery can be improved by 1 percent to 2 percent; the interface and electrochemical performance of the lithium battery can be obviously improved.'
    res = rag_llm.response(query, context)
    print(res)

    from src.giga_chat.prompts.local_patent_prompts import ru_en_translation_prompt, en_ru_translation_prompt, \
    questions_to_text_prompt

    pr = ru_en_translation_prompt.format(text=res)
    res_2  = rag_llm.simple_response(pr)
    print(res_2)

    pr = en_ru_translation_prompt.format(text=res_2)
    res_3 = rag_llm.simple_response(pr)
    print(res_3)

    pr = questions_to_text_prompt.format(text=res_3)
    res_4 = rag_llm.simple_response(pr)
    print(res_4)
