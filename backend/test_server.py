"""
Minimal test server with just fish classification
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
import os
from services.fish_classification import predict_image

app = FastAPI(title="Fish Classification Test API")

@app.get("/")
def root():
    return {"message": "Fish Classification Test API is running"}

@app.post("/classify/fish")
async def classify_fish(file: UploadFile = File(...)):
    """
    Classify a fish image.
    """
    try:
        # Save the uploaded file temporarily
        file_path = os.path.join("data", file.filename)
        os.makedirs("data", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # Predict the class of the image
        predicted_class, confidence = predict_image(file_path)
        
        # Clean up the temporary file
        os.remove(file_path)
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error classifying image: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run("test_server:app", host="127.0.0.1", port=8000, reload=True)
