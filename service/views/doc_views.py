from django.shortcuts import render
from django.conf import settings
from service.models import Doc    # Alias to differentiate from python-docx Document
import os
from docx import Document as DocxDocument
from docx.opc.constants import RELATIONSHIP_TYPE as RT
def analyze_document(request, doc_id):
    document = Doc.objects.get(id=doc_id)  # Use the aliased model name here
    docx = DocxDocument(document.doc_file.path)

    # Extract text
    text_content = [para.text for para in docx.paragraphs]

    # Extract tables
    tables = []
    for table in docx.tables:
        table_content = []
        for row in table.rows:
            row_data = [cell.text for cell in row.cells]
            table_content.append(row_data)
        tables.append(table_content)

    # Extract images
    images = []
    # Accessing images requires checking relationship types
    for rel in docx.part.rels.values():
        if rel.reltype == RT.IMAGE:
            image = rel.target_part.blob
            image_filename = os.path.basename(rel.target_part.partname)
            image_path = os.path.join(settings.MEDIA_ROOT, 'doc_images', image_filename)
            with open(image_path, 'wb') as img_file:
                img_file.write(image)
            images.append(os.path.join(settings.MEDIA_URL, 'doc_images', image_filename))

    context = {
        'text_content': text_content,
        'tables': tables,
        'images': images
    }

    return render(request, 'document_analysis.html', context)
