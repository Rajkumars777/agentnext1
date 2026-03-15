import os
import shutil
import subprocess
import sys

def run_command(cmd, cwd=None):
    print(f"Running: {cmd}")
    process = subprocess.run(cmd, shell=True, cwd=cwd)
    if process.returncode != 0:
        print(f"Error: Command failed with return code {process.returncode}")
        sys.exit(1)

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, "frontend")
    backend_dir = os.path.join(project_root, "src")
    static_dir = os.path.join(backend_dir, "static")

    # 1. Build Frontend
    print("--- Building Frontend ---")
    run_command("npm install", cwd=frontend_dir)
    run_command("npm run build", cwd=frontend_dir)

    # 2. Copy Frontend to Backend Static
    print("--- Copying Frontend to Backend ---")
    if os.path.exists(static_dir):
        shutil.rmtree(static_dir)
    
    frontend_out = os.path.join(frontend_dir, "out")
    if not os.path.exists(frontend_out):
        # Check if it's named 'dist' or something else
        print(f"Error: Next.js build output not found at {frontend_out}")
        sys.exit(1)
        
    shutil.copytree(frontend_out, static_dir)

    # 3. Install PyInstaller if missing
    print("--- Preparing PyInstaller ---")
    run_command(f"{sys.executable} -m pip install pyinstaller")

    # 4. Build EXE
    print("--- Building Standalone EXE ---")
    # We include 'src/static' as data
    pyinstaller_cmd = (
        f"{sys.executable} -m PyInstaller --onefile --noconsole --clean "
        f"--add-data \"src/static;src/static\" "
        f"--add-data \"src/api;src/api\" "
        f"--add-data \"src/core;src/core\" "
        f"--name NEXUS_Agent "
        f"src/desktop_main.py"
    )
    run_command(pyinstaller_cmd)

    print("--- Build Complete ---")
    print(f"Your standalone executable is located in: {os.path.join(project_root, 'dist', 'NEXUS_Agent.exe')}")

if __name__ == "__main__":
    main()
