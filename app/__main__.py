import sys
import time
from app import RAG
from app.singletons import get_chromadb
from rich.traceback import install

install(show_locals=True)


def wait_or_pull(interval=3600):
    start_time = time.time()
    while time.time() - start_time < interval:
        user_input = (
            input("Type 'pull' to run update inmediately or 'q' to quit\n")
            .strip()
            .lower()
        )
        if user_input == "pull":
            return
        elif user_input == "q":
            print("Exiting...")
            sys.exit(0)
    time.sleep(1)


def run():
    rag = RAG(get_chromadb())
    while True:
        rag.update_files()
        wait_or_pull()
