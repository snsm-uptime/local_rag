import debugpy
from watchfiles import run_process
import subprocess


def run():
    subprocess.run(["python", "-Xfrozen_modules=off", "-m", "app"])


if __name__ == "__main__":
    print("🔧 Waiting for debugger to attach on port 5678...")
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()
    print("✅ Debugger attached!")

    print("👀 Watching for code changes in /app/app...")
    run_process("app", target=run)
