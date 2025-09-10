# Integration Steps for Fish Classification

## 1. Project Structure Setup
- ✅ Created models directory
- ✅ Created models/fish_classification directory for the model
- ✅ Created necessary Python modules and packages

## 2. Model Transfer
- ✅ Copied the fish classification model from SIH Hackathon to the new location
- ✅ Set up the model in the new structure with proper imports

## 3. Service Integration
- ✅ Updated the fish_classification.py service to use the new model structure
- ✅ Main.py already has the proper imports and endpoints

## 4. Additional Steps
1. **Start the Server**:
   ```
   cd c:\Users\VICTUS\Desktop\SIH Hackathon\ocean-ai-prototype\backend
   python -m uvicorn main:app --reload
   ```

2. **Test the Fish Classification Endpoint**:
   - Use an API testing tool like Postman or curl
   - Send a POST request to http://localhost:8000/classify/fish with an image file
   - Or use the Swagger UI at http://localhost:8000/docs

3. **Model Maintenance**:
   - The model is now in a dedicated folder at models/fish_classification
   - To update the model, replace the .h5 file in that folder
   - The class names are hardcoded in model.py

## 5. Troubleshooting
If you encounter issues:
1. Check that TensorFlow is installed: `pip install tensorflow`
2. Verify the model file exists at the correct path
3. Check the console for specific error messages
4. Make sure PIL (Pillow) is installed: `pip install Pillow`

## 6. Documentation
- The fish classification service accepts image files and returns the predicted species and confidence level
- Supported fish species: Black Sea Sprat, Gilt-Head Bream, Hourse Mackerel, Red Mullet, Red Sea Bream, Sea Bass, Shrimp, Striped Red Mullet, Trout
