from datetime import datetime
from functools import partial
from pathlib import Path

import pdfplumber
from rich.console import Console

from app.constants import DOCUMENTS_FOLDER, PROMPTS_FOLDER

console = Console()


def read_local_file(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        try:
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                return text.strip()
        except Exception as e:
            console.print(f"[red]Error reading PDF: {e}[/red]")
            return ""

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        console.print(f"[red]Text decode error in file: {file_path}[/red]")
        return ""
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        return ""


def split_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def get_files_from_folder(folder: str) -> list:
    folder = Path(folder)
    folder.mkdir(exist_ok=True)

    files_metadata = []
    for file in folder.glob("**/*"):
        if file.is_file():
            files_metadata.append(
                {
                    "path": str(file.resolve()),
                    "name": file.name,
                    "modified": datetime.fromtimestamp(
                        file.stat().st_mtime
                    ).isoformat(),
                }
            )
    console.print(files_metadata)
    return files_metadata


list_local_files = partial(get_files_from_folder, DOCUMENTS_FOLDER)


def get_prompt(prompt_name: str) -> str:
    prompt_file = Path(PROMPTS_FOLDER) / f"{prompt_name}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file '{prompt_name}.md' not found in prompts/")
    return prompt_file.read_text(encoding="utf-8")
