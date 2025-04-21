import sys
import time
from app import RAG
from app.singletons import get_chromadb
from rich.traceback import install

install(show_locals=True)


def wait_or_pull(interval=3600):
    start_time = time.time()
    while time.time() - start_time < interval:
        time.sleep(1)


def run():
    rag = RAG(get_chromadb())
    while True:
        rag.update_files()
        wait_or_pull()


if __name__ == "__main__":
    run()
