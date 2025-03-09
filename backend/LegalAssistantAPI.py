from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from LegalAssistant import LegalAssistant  # Import the LegalAssistant class
from fastapi.middleware.cors import CORSMiddleware
import logging

class LegalAssistantAPI:
    def __init__(self):
        logging.info("Initializing LegalAssistantAPI")
        print("Initializing LegalAssistantAPI")
        self.app = FastAPI()
        self.legal_assistant = LegalAssistant()  # Initialize the LegalAssistant instance
        self._setup_routes()
        self._setup_cors()
        
    def _setup_cors(self):
        """Configure CORS middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Add your React app's URL
            allow_credentials=True,
            allow_methods=["*"],  # Allow all HTTP methods
            allow_headers=["*"],  # Allow all headers
        )

    def _setup_routes(self):
        """Define all the routes for the application."""
        @self.app.post("/get-legal-answer")
        async def get_legal_answer(request: self.QueryRequest):
            try:
                print(f"Request query: {request}")
                logging.info(f"Request query: {request}")
                response = self.legal_assistant.get_legal_answer(request)
                return {"answer": response}
            except Exception as e:
                logging.error(str(e))
                print(str(e))
                raise HTTPException(status_code=500, detail="Server Error")

        @self.app.get("/test/")
        async def test():
            return {"message": "Hello World!"}

    class QueryRequest(BaseModel):
        query: str

