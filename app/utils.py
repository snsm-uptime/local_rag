from datetime import datetime
from functools import partial
from pathlib import Path

import easyocr
import numpy as np
import pdfplumber
from pdf2image import convert_from_path
from rich.console import Console

from app.constants import DOCUMENTS_FOLDER, OCR_LANG, PROMPTS_FOLDER

console = Console()


def extract_pdf_to_txt(pdf_path: str) -> str:
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=300, thread_count=10)
    reader = easyocr.Reader([OCR_LANG], gpu=False)

    # Use list as a string builder
    text_lines = []

    for i, image in enumerate(images):
        print(f"🔍 Processing page {i + 1}")
        result = reader.readtext(np.array(image), detail=0)
        page_text = "\n".join(result)
        text_lines.append(f"\n\n--- Page {i + 1} ---\n{page_text}")

    return "".join(text_lines)


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
