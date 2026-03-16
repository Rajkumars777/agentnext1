import os
import shutil
import subprocess
import sys
import platform

def run_command(cmd, cwd=None):
    print(f"Running: {cmd}")
    process = subprocess.run(cmd, shell=True, cwd=cwd)
    if process.returncode != 0:
        print(f"Error: Command failed with return code {process.returncode}")
        sys.exit(1)

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, "frontend")
    target_dir = os.path.join(frontend_dir, "src-tauri")

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Tauri sidecar naming convention: {bin-name}-{target-triple}{extension}
    # For Windows x64: ai-engine-x86_64-pc-windows-msvc.exe
    target_triple = "x86_64-pc-windows-msvc"
    binary_name = f"ai-engine-{target_triple}.exe"

    print(f"--- Building Sidecar: {binary_name} ---")

    # Install PyInstaller
    run_command(f'"{sys.executable}" -m pip install pyinstaller')

    # Build the backend as a single EXE
    # We bundle the 'src' directory so imports like 'from src.api...' work.
    pyinstaller_cmd = (
        f'"{sys.executable}" -m PyInstaller --onefile --noconsole --clean '
        f'--add-data "src;src" '
        f'--name {binary_name} '
        f'src/main.py'
    )
    
    run_command(pyinstaller_cmd)

    # Move the binary to the tauri binaries folder
    source_binary = os.path.join(project_root, "dist", binary_name)
    destination_binary = os.path.join(target_dir, binary_name)

    print(f"Moving {source_binary} to {destination_binary}")
    if os.path.exists(destination_binary):
        os.remove(destination_binary)
    shutil.move(source_binary, destination_binary)

    print("--- Sidecar Build Complete ---")

if __name__ == "__main__":
    main()
