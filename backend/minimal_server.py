"""
Very minimal test server
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Minimal Test API")

@app.get("/")
def root():
    return {"message": "Minimal Test API is running"}

if __name__ == "__main__":
    uvicorn.run("minimal_server:app", host="127.0.0.1", port=8000, reload=True)
