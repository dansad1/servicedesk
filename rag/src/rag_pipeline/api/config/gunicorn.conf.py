import os
import signal

from rag_pipeline.api.config.sgi_config import sgi_config

wsgi_app = sgi_config.WSGI_APP
bind = f"{sgi_config.HOST}:{sgi_config.PORT}"
workers = sgi_config.WORKERS_COUNT
worker_class = sgi_config.WORKER_CLASS
reload = sgi_config.AUTO_RELOAD
timeout = 60 * 60 * 24

current_file_path = os.path.abspath(__file__)

# Вывод пути к текущему файлу
print("===============",current_file_path, "===============")

def worker_int(worker):
    os.kill(worker.pid, signal.SIGINT)
