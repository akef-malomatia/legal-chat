from pydantic import BaseModel
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from myOpenAI import GPT_4o
import os
from dotenv import load_dotenv

class QueryRequest(BaseModel):
    query: str

class LegalAssistant:

    def get_formatted_sources(self, query):
        load_dotenv()
        # Initialize Azure Search Client
        search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
        search_client = SearchClient(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            index_name=os.getenv("INDEX_NAME"),
            credential=AzureKeyCredential(search_api_key)
        )

        # Retrieve search results
        search_results = search_client.search(
            search_text=query,
            top=5,
        )

        # Format sources
        sources_formatted = "\n".join([
            f'{document["title"]}:{document["chunk"]}:{document["@search.score"]}' for document in search_results
        ])

        return sources_formatted

    def get_legal_answer(self, request: QueryRequest):
        gpt_4o = GPT_4o()
        
         # Define the grounded prompt template
        grounded_prompt = """
            You are a friendly assistant providing legal information based on the laws of Qatar.
            Answer the query using only the sources provided below in a professional and concise manner.
            Answer ONLY with the information listed in the list of sources below.
            If there isn't enough information below, state that you don't know.
            Do not generate answers that don't rely on the sources below.
            Query: {query}
            Sources:\n{sources}
            """

        system_msg = "You are a Qatari Lawyer"
        user_msg = grounded_prompt.format(query=request.query, sources=self.get_formatted_sources(request.query))

        response = gpt_4o.send_msg(system_msg, user_msg)

        return {"answer": response}
