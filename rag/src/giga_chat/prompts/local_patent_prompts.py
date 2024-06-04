from langchain.prompts import PromptTemplate


ru_en_translation_prompt = PromptTemplate(
    input_variables=['text'],
    template='''
Translate this text into English. The answer should contain only a translation of the text without additional explanations. There is no need to explain that this is a translated text.
text:`{text}`
'''
)

en_ru_translation_prompt = PromptTemplate(
    input_variables=['text'],
    template='''
Translate this text into Russian. The answer should contain only a translation of the text without additional explanations. There is no need to explain that this is a translated text.
text:`{text}`
'''
)

questions_to_text_prompt = PromptTemplate(
    input_variables=['text'],
    template='''
Придумай несколько вопросов на который отвечает данный текст. Ответ должен содержать только придуманные тобой вопросы, через запятую.
текст:`{text}`
'''
)

context_compression_prompt= PromptTemplate(
    input_variables=['text'],
    template='''
Придумай несколько вопросов к тексту и напиши ответы на них. Перечисли вопросы и ответы через запятую.
текст:`{text}`
'''
)

get_id_prompt = PromptTemplate(
    input_variables=['text'],
    template='''
"Ты — русскоязычный автоматический ассистент патентного отдела. Ты помогаешь людям находить точную информацию в тексте отчета. "
    "Отвечай на вопрос пользователя только на основе информации из отчета. Если фрагмент отчета не содержит "
    "релевантной информации, отвечай: не достаточно информации для ответа."
текст:`{text}`
'''
)

