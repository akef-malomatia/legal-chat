from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer,
    FieldMapping,
    FieldMappingFunction,
    IndexingParameters,
    IndexingParametersConfiguration,
    BlobIndexerParsingMode,
)
from azure.core.credentials import AzureKeyCredential

import os
from dotenv import load_dotenv
from azure.core.exceptions import HttpResponseError


class AzureSearchIndexer:
    def __init__(self, endpoint, credential, index_name, skillset_name, data_source_name, indexer_name):
        self.client = SearchIndexerClient(endpoint, credential)
        self.index_name = index_name
        self.skillset_name = skillset_name
        self.data_source_name = data_source_name
        self.indexer_name = indexer_name

    def create_indexer(self):
        try:
            # Use existing fields in your index (e.g., 'chunk' and 'title') for output field mappings
            indexer_parameters = IndexingParameters(
                configuration=IndexingParametersConfiguration(
                    parsing_mode=BlobIndexerParsingMode.DEFAULT,
                    query_timeout=None,
                    first_line_contains_headers=True,
                    image_action="generateNormalizedImages"
                )
            )

            indexer = SearchIndexer(
                name=self.indexer_name,
                description="Indexer to index documents and generate embeddings",
                skillset_name=self.skillset_name,
                target_index_name=self.index_name,
                data_source_name=self.data_source_name,
                parameters=indexer_parameters,
                field_mappings=[
                    # FieldMapping(
                    #     source_field_name="metadata_storage_name",
                    #     target_field_name="title",
                    #     mapping_function=None
                    # ),
                ],
                output_field_mappings=[]
            )

            result = self.client.create_or_update_indexer(indexer)
            print(f"Indexer '{result.name}' created successfully.")
            return result
        except HttpResponseError as e:
            print(f"Failed to create indexer: {e}")
            raise

    def run_indexer(self):
        # TO-DO: showed know when the indexer is finished running.
        try:
            self.client.run_indexer(self.indexer_name)
            print(f"Indexer '{self.indexer_name}' is running successfully.")
        except HttpResponseError as e:
            print(f"Failed to run indexer: {e}")
            raise

# Example usage
if __name__ == "__main__":
    load_dotenv()
    # Replace these with actual values
    endpoint = os.getenv("SEARCH_ENDPOINT")
    api_key = os.getenv("SEARCH_API_KEY")
    index_name = os.getenv("INDEX_NAME")
    skillset_name = f"{index_name}-skillset"
    data_source_name = f"{index_name}-blob"

    manager = AzureSearchIndexer(
        endpoint,
        AzureKeyCredential(api_key),
        index_name,
        skillset_name,
        data_source_name,
    )

    try:
        manager.create_indexer()
        manager.run_indexer()
    except Exception as e:
        print(f"An error occurred: {e}")
