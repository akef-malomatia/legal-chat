import openai
from openai import AzureOpenAI
from azure.search.documents.models import VectorQuery
from typing import List

class AdaModel:
    def __init__(self, api_key, api_version, azure_endpoint):
        # Load environment variables for API keys
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
        
    def encode(self, query: str)-> List[VectorQuery]:
        """
        Encodes a query into a vector using the OpenAI Ada model.

        Args:
            query (str): The query to be encoded into a vector.

        Returns:
            list: A vector representing the query, or None if an error occurs.
        """
        try:
            azure_openai_embedding_dimensions = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS"))
            # Call OpenAI's Embedding API
            print("Sending to AdaS")
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",  # Ada embedding model
                input=query,
                # dimensions=azure_openai_embedding_dimensions
            )
            # Extract the embedding from the response
            embedding = response.data[0].embedding
            return embedding
        
        except Exception as e:
            print(f"Error encoding query to vector: {e}")
            return None

    def encode_batch(self, queries: list):
        """
        Encodes a batch of queries into vectors using the OpenAI Ada model.

        Args:
            queries (list): A list of queries to be encoded.

        Returns:
            list: A list of vectors representing each query, or None if an error occurs.
        """
        try:
            # Call OpenAI's Embedding API for a batch of queries
            response = openai.Embedding.create(
                model="text-embedding-ada-002",  # Ada embedding model
                input=queries
            )
            # Extract embeddings for all queries
            embeddings = [item['embedding'] for item in response['data']]
            return embeddings
        
        except Exception as e:
            print(f"Error encoding queries to vectors: {e}")
            return None
