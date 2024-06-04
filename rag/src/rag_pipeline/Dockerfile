FROM python:3.9-slim

WORKDIR /opt/app-root/rag/src/

COPY rag/src/rag_pipeline/requirements.txt /opt/app-root/rag/src/rag_pipeline/

RUN pip install --no-cache-dir -r /opt/app-root/rag/src/rag_pipeline/requirements.txt

ENV PYTHONPATH /opt/app-root/rag/src
ENV PYTHONUNBUFFERED=1


RUN pwd && ls -l


CMD ["gunicorn", "--config", "/opt/app-root/rag/src/rag_pipeline/api/config/gunicorn.conf.py"]