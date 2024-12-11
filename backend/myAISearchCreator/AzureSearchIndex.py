from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SemanticConfiguration,
    SemanticSearch,
    SemanticPrioritizedFields,
    SemanticField,
    SearchIndex,
)
from azure.core.credentials import AzureKeyCredential

import os
from dotenv import load_dotenv


class AzureSearchIndex:
    def __init__(self, endpoint: str, credential, index_name: str, openai_config: dict):
        self.index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
        self.index_name = index_name
        self.ada_config = openai_config

    def create_index(self):
        # Define the fields for the index
        fields = [
            SearchField(
                name="chunk_id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=False,
                facetable=False,
                stored=True,
                analyzer_name="keyword",
            ),
            SearchField(
                name="parent_id",
                type=SearchFieldDataType.String,
                searchable=False,
                filterable=True,
                facetable=False,
                sortable=False,
                stored=True,
            ),
            SearchField(
                name="chunk",
                type=SearchFieldDataType.String,
                filterable=False,
                sortable=False,
                facetable=False,
                stored=True,
            ),
            SearchField(
                name="title",
                type=SearchFieldDataType.String,
                filterable=False,
                facetable=False,
                sortable=False,
                stored=True,
            ),
            # SearchField(
            #     name="languageCode",
            #     type=SearchFieldDataType.String,
            #     filterable=False,
            #     facetable=False,
            #     sortable=False,
            #     retrievable=True,
            #     stored=True,
            # ),
            # SearchField(
            #     name="languageName",
            #     type=SearchFieldDataType.String,
            #     filterable=False,
            #     facetable=False,
            #     sortable=False,
            #     retrievable=True,
            #     stored=True,
            # ),
            SearchField(
                name="vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                filterable=False,
                facetable=False,
                sortable=False,
                # retrievable=True,
                stored=True,
                vector_search_dimensions=1536,
                vector_search_profile_name=f"{self.index_name}-vector-profile"
            ),
        ]

        # Configure vector search with HNSW algorithm
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name=f"{self.index_name}-algorithm",
                    # metric="cosine",  # Define only recognized attributes
                    # ef_construction=400,
                    # m=4,
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name=f"{self.index_name}-vector-profile",
                    algorithm_configuration_name=f"{self.index_name}-algorithm",
                    vectorizer_name=f"{self.index_name}-vectorizer",
                )
            ],
            vectorizers=[
                AzureOpenAIVectorizer(
                    vectorizer_name=f"{self.index_name}-vectorizer",
                    kind="azureOpenAI",
                    parameters=AzureOpenAIVectorizerParameters(
                        resource_url=self.ada_config["endpoint"],
                        deployment_name=self.ada_config["deployment_id"],
                        model_name=self.ada_config["model_name"],
                        api_key=self.ada_config["api_key"],
                    ),
                )
            ],
        )

        # Configure semantic search
        semantic_config = SemanticConfiguration(
            name=f"{self.index_name}-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                content_fields=[SemanticField(field_name="chunk")],
            ),
        )
        semantic_search = SemanticSearch(configurations=[semantic_config])

        # Create the search index
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
            semantic_search=semantic_search,
        )

        # Create or update the index
        result = self.index_client.create_or_update_index(index)
        print(f"Index '{result.name}' created successfully.")


# Example usage of the class
if __name__ == "__main__":
    load_dotenv()
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    credential = AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
    index_name = "law2006"
    azure_ada_openai_config = {
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "deployment_id": "text-embedding-ada-002",
        "model_name": "text-embedding-ada-002",
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
    }

    # Create the index
    law_index = AzureSearchIndex(endpoint, credential, index_name, azure_ada_openai_config)
    law_index.create_index()
