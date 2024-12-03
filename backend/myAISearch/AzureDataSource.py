from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataSourceConnection, 
    SearchIndexerDataSourceType,
    SearchIndexerDataContainer
)

import os
from dotenv import load_dotenv

class AzureDataSource:
    def __init__(self, search_endpoint, credential):
        self.indexer_client = SearchIndexerClient(endpoint=search_endpoint, credential=credential)

    def create_data_source(self, data_source_name):

        container = SearchIndexerDataContainer(name=os.getenv("CONTAINER_NAME"))
        
        data_source = SearchIndexerDataSourceConnection(
            name=data_source_name,
            type=SearchIndexerDataSourceType.ADLS_GEN2,
            connection_string=os.getenv("AZURE_BLOB_CONNECTION_STRING"),
            container=container,
            description="LAW NO. 22 of 2006 PROMULGATING 'THE FAMILY LAW'",
            # data_deletion_detection_policy=SoftDeleteColumnDeletionDetectionPolicy(soft_delete_column_name="IsDeleted", soft_delete_marker_value="True")
        )
        # Create the data source connection in Azure
        self.indexer_client.create_data_source_connection(data_source)
        print(f"Data source '{data_source_name}' created successfully.")

if __name__ == "__main__":
    load_dotenv()
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_api_key = os.getenv("AZURE_SEARCH_API_KEY")

    # Initialize Azure Search Document Integration
    azure_search = AzureDataSource(search_endpoint, AzureKeyCredential(search_api_key))

    index_name="law2006"
    data_source_name = f"{index_name}-blob"

    # Step 1: Create data source
    azure_search.create_data_source(data_source_name)
