import uvicorn
from LegalAssistantAPI import LegalAssistantAPI
from flask_cors import CORS  # Import CORS

# Expose the app as a top-level variable
api_app = LegalAssistantAPI()
app = api_app.app

if __name__ == "__main__":
    # Use uvicorn to run the app
    uvicorn.run("main:app", host="localhost", port=3001, reload=True)
