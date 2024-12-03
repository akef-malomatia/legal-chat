from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from LegalAssistant import LegalAssistant  # Import the LegalAssistant class

class LegalAssistantAPI:
    def __init__(self):
        # Initialize FastAPI app
        self.app = FastAPI()
        self.legal_assistant = LegalAssistant()  # Initialize the LegalAssistant instance
        self._setup_routes()

    def _setup_routes(self):
        """Define all the routes for the application."""
        
        @self.app.post("/get-legal-answer/")
        async def get_legal_answer(request: self.QueryRequest):
            try:
                # Use the initialized LegalAssistant instance to get the answer
                response = self.legal_assistant.get_legal_answer(request)
                return {"answer": response}
            except Exception as e:
                print(str(e))
                raise HTTPException(status_code=500, detail="Server Error")
        
        @self.app.get("/test")
        async def test():
            """A simple test endpoint."""
            return {"message": "Hello World!"}

    class QueryRequest(BaseModel):
        query: str

    def run(self, host="0.0.0.0", port=8000):
        """Run the FastAPI application using Uvicorn."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


