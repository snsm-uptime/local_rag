from ollama import chat
from app.utils import console, get_prompt
from app.constants import CHAT_NAME
from app.messages import NOT_FOUND
from singletons import get_chromadb


def ollama_chat(system_message: str, query: str, context: str) -> str:
    try:
        response = chat(
            model="deepseek-r1:1.5b",
            messages=[
                {
                    "role": "system",
                    "content": f"{system_message}\n\nContext: {context}",
                },
                {"role": "user", "content": query},
            ],
            stream=False,
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"


def chat_agent(query: str) -> str:
    db = get_chromadb()
    system_message = get_prompt("study_buddy")
    query_embedding = db.get_embedding(query)
    if query_embedding is None:
        return "Error obtaining query embedding."

    try:
        results = db.collection.query(query_embeddings=[query_embedding], n_results=3)
    except Exception as e:
        return f"Error querying ChromaDB: {str(e)}"

    if not results or "documents" not in results or not results["documents"]:
        return NOT_FOUND

    documents = results["documents"][0]
    context = " ".join(documents)
    if not context.strip():
        return NOT_FOUND

    return ollama_chat(system_message, query, context)


def run():
    console.rule(f"[bold magenta]{CHAT_NAME}[/]")
    console.print("[bold green]Type 'exit' to quit.[/]\n")
    while True:
        query = console.input("[bold cyan]Your Question> [/]").strip()
        if query.lower() in ("exit", "quit", "q"):
            break
        answer = chat_agent(query)
        console.print(f"\n[bold yellow]Answer:[/]\t{answer}")


if __name__ == "__main__":
    run()
