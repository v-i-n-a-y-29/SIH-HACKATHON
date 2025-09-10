import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def main():
    # Get the current directory
    current_dir = Path(__file__).resolve().parent
    
    # Make sure data directory exists
    data_dir = current_dir / "data"
    if not data_dir.exists():
        os.makedirs(data_dir, exist_ok=True)
        print(f"Created data directory at {data_dir}")
    
    # Check if environment is set up
    try:
        import fastapi
        import uvicorn
        print("FastAPI and Uvicorn are installed. Starting server...")
    except ImportError:
        print("Installing required dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start the server in a separate process
    print("\nStarting Ocean AI Prototype server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=current_dir
    )
    
    # Wait for the server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    # Open browser to the API docs
    api_url = "http://localhost:8000/docs"
    print(f"\nOpening API documentation at {api_url}")
    webbrowser.open(api_url)
    
    try:
        print("\nPress Ctrl+C to stop the server...\n")
        server_process.wait()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    main()
