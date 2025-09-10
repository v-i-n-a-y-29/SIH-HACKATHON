# backend/run_server.py
import uvicorn
import logging
import sys
import os
import time

# Configure logging to show detailed errors
logging.basicConfig(level=logging.DEBUG)

def run_server():
    """Run the server with proper error handling"""
    try:
        # Print clear message about server startup
        print("=" * 50)
        print("🌊 Ocean AI Backend Server Starting...")
        print("🚀 API Documentation: http://127.0.0.1:8000/docs")
        print("🔬 Root endpoint: http://127.0.0.1:8000/")
        print("=" * 50)
        
        # Run the server with auto-reload for development and debug logging
        uvicorn.run(
            "app.main:app", 
            host="127.0.0.1", 
            port=8000,  # Use standard port 8000
            log_level="info",
            reload=True  # Enable auto-reload for development
        )
    except KeyboardInterrupt:
        print("\nServer shutdown requested by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_server()
