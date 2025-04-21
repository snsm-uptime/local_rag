import subprocess
import sys

import debugpy
from rich import print
from watchfiles import run_process

WATCH_DIR = "app"


def run_target():
    target = sys.argv[1] if len(sys.argv) > 1 else "entrypoints/run_backend.py"
    subprocess.run(["python", "-Xfrozen_modules=off", f"app/{target}"])


if __name__ == "__main__":
    print(
        "🔧 [bold yellow]Waiting for debugger to attach on port 5678...[/bold yellow]"
    )
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()
    print("✅ [bold green]Debugger attached![/bold green]")

    print(f"👀 [blue]Watching for changes in '{WATCH_DIR}/'...[/blue]")
    run_process(WATCH_DIR, target=run_target)
