import pandas as pd
from docx import Document
from pypdf import PdfReader


def read_xlsx(file_path: str):
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    dict_array = df.to_dict('records')
    return dict_array


def read_txt(file_path: str):
    with open(file_path, encoding='utf-8', mode='r') as f:
        text = f.read()
    return text


def read_docx(file_path: str):
    document = Document(file_path)
    return '\n'.join([p.text for p in document.paragraphs]  )


def read_pdf(file_path: str):
    reader = PdfReader(file_path)
    return '\n'.join(p.extract_text() for p in reader.pages)


def read_meta_file(file_path: str):
    if file_path.endswith('txt'):
        return read_txt(file_path)
    if file_path.endswith('pdf'):
        return read_pdf(file_path)
    if file_path.endswith('docx'):
        return read_docx(file_path)
    if file_path.endswith('xlsx'):
        return read_xlsx(file_path)
    return ''


if __name__ == '__main__':
    #print(read_xlsx(r'C:\Users\Gleb\PycharmProjects\patent-rag\Реестр патентов 26.04.2024.xlsx')[0].keys())
    #print(read_docx(r'C:\Users\Gleb\PycharmProjects\patent-rag\moodle_data\ТЕМА 5. Сделки.docx'))
    print(read_pdf(r'C:\Users\Gleb\PycharmProjects\patent-rag\moodle_data\Тема 2 Конспект Гражданское правоотношение.pdf'))