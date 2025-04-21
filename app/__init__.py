import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from pydantic import FilePath
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from sentence_transformers import SentenceTransformer

from app.constants import (
    COLLECTION_NAME,
    DOCUMENTS_FOLDER,
    PERSISTENT_DIRECTORY,
    PROCESSED_FILES_PATH,
)
from app.utils import (
    console,
    list_local_files,
    read_local_file,
    split_text,
    extract_pdf_to_txt,
)
from app.singletons import ChromaDB


class RAG:
    def __init__(self, db: ChromaDB):
        self.db = db

    @property
    def processed(self) -> dict:
        return self.load_processed_files()

    def load_processed_files(self) -> dict:
        if os.path.exists(PROCESSED_FILES_PATH):
            with open(PROCESSED_FILES_PATH, "r") as f:
                return json.load(f)
        return {}

    def save_processed_files(self, processed):
        with open(PROCESSED_FILES_PATH, "w") as f:
            json.dump(processed, f, indent=2)

    def process_file(self, file_path: str):
        f = Path(file_path)
        file_name = f.name
        console.rule(f"[bold blue]Processing file: {file_name}")
        content = read_local_file(os.path.join(DOCUMENTS_FOLDER, file_name))
        if not content:  # Evaluate OCR results
            console.rule(f"[orage]NO text content for file: {file_name}[/orage]")
            console.print(f"[magenta]Running OCR...[/magenta]")
            ocr_text = extract_pdf_to_txt(pdf_path=file_path)
            if ocr_text != "":
                console.print(
                    f"[green]OCR text extracted successfully.[/green][orange]{len(ocr_text)} chars[/orange]"
                )
                content = ocr_text
        chunks = split_text(content)
        console.rule(f"[green]Split text into {len(chunks)} chunks.[/green]")

        vector_ids = []
        for i, chunk in enumerate(chunks):
            embedding = self.db.get_embedding(chunk)
            if embedding is None:
                continue

            vector_id = f"{file_name}_{i}"
            vector_ids.append(vector_id)

            metadata = {"file_name": file_name, "chunk_index": i, "text": chunk[:200]}

            try:
                print(embedding)
                self.db.collection.add(
                    embeddings=(embedding),
                    metadatas=metadata,
                    documents=chunk,
                    ids=[vector_id],
                )
                console.print(f"[green]Userted chunk {i} successfully.[/green]")
            except Exception as e:
                console.print(f"[red]Error upserting vector: {e}.[/red]")

        processed = self.load_processed_files()
        processed[file_name] = {
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            "vectors": vector_ids,
            "name": file_name,
        }

        self.save_processed_files(processed)

        console.print(
            f"[bold green]File processed & upserted to ChromaDB.[/bold green]\n"
        )

    def delete_vectors(self, file_name: str) -> bool:
        processed = self.load_processed_files()
        file_data = processed.get(file_name, {})
        status = False
        try:
            self.db.collection.delete(where={"file_name": file_name})
            console.print(
                f"[green]Used metadata to delete vectors for {file_data}[/green]"
            )
            status = True
        except Exception as e:
            console.print(f"[red]Metadata filter deletion failed: {e}[/red]")
        return status

    def update_files(self):
        console.print(f"\n=== Update started {datetime.now().isoformat()} ===\n")
        processed = self.load_processed_files()

        try:
            for file_name in list(processed.keys()):
                file_path = os.path.join(DOCUMENTS_FOLDER, file_name)
                if not Path(file_path).exists():
                    console.print(f"Removing vectors for deleted file: {file_name}")
                    if self.delete_vectors(file_name):
                        del processed[file_name]
                        self.save_processed_files(processed)

            current_files = list_local_files()

            for file in current_files:
                fname = file["name"]
                existing = processed.get(fname)
                if (not existing) or (file["modified"] > existing["modified"]):
                    console.print(f"Deleting old vectors for: {fname}")
                    self.delete_vectors(fname)
                    self.process_file(os.path.join(DOCUMENTS_FOLDER, fname))
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
