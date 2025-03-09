from azure.cosmos import CosmosClient
from AzureDataSource import AzureDataSource
from AzureSearchIndex import AzureSearchIndex
from AzureSearchIndexer import AzureSearchIndexer
from AzureSkillset import AzureOpenAISkillset
from azure.core.credentials import AzureKeyCredential

import os
from dotenv import load_dotenv

load_dotenv()

# Cosmos DB details
# cosmos_endpoint = os.getenv("COSMOS_DB_ENDPOINT")
# cosmos_key = os.getenv("COSMOS_DB_PRIMARY_KEY")
# database_name = "config-database"
# container_name = "config-container"

# Initialize Cosmos client and fetch the configuration
# client = CosmosClient(cosmos_endpoint, cosmos_key)
# database = client.get_database_client(database_name)
# container = database.get_container_client(container_name)

# Fetch configuration document by "rg-ai01"
# config_item = container.read_item(item="rg-ai01", partition_key="rg-ai01")

# Extract values from the configuration document
analyzeDocumentAzureFunc_url = os.getenv("ANALYZE_DOCUMENT_AZURE_FUNC_URL")
splitDocumentAzureFunc_url = os.getenv("SPLIT_DOCUMENT_AZURE_FUNC_URL")

# search_endpoint = config_item["ai_search"]["endpoint"]
# search_api_key = config_item["ai_search"]["api_key"]
# cases_index_name = config_item["ai_search"]["cases_index_name"]
# laws_index_name = config_item["ai_search"]["laws_index_name"]

search_endpoint = os.getenv("SEARCH_ENDPOINT")
search_api_key = os.getenv("SEARCH_API_KEY")
index_name = os.getenv("INDEX_NAME")

openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
ada_deployment_name = os.getenv("AZURE_OPENAI_EMBEDDER_MODEL")
embedding_dimensions = os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS")
openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")

# cases_container_name = config_item["storage_account"]["cases_container_name"]
# laws_container_name = config_item["storage_account"]["laws_container_name"]
# connection_string = config_item["storage_account"]["blob_connection_string"]

credential = AzureKeyCredential(search_api_key)
azure_ada_openai_config = {
    "endpoint": openai_endpoint,
    "deployment_id": ada_deployment_name,
    "model_name": ada_deployment_name,
    "api_key": openai_api_key,
    "dimensions": embedding_dimensions,
}

def createAzureSearchItems(index_name, container_name = None):
    data_source_name = f"{index_name}-blob"
    skillset_name = f"{index_name}-skillset"
    indexer_name = f"{index_name}-indexer"

    # Step 1: Create data source
    # try:
    #     azureSearch = AzureDataSource(search_endpoint, AzureKeyCredential(search_api_key))
    #     azureSearch.create_data_source(data_source_name, container_name, connection_string)
    # except Exception as e:
    #     print(f"Error creating data source: {e}")

    # Step 2: Create the index
    try:
        law_index = AzureSearchIndex(search_endpoint, credential, index_name, azure_ada_openai_config)
        law_index.create_index()
    except Exception as e:
        print(f"Error creating index: {e}")

    # Step 3: Create the skillset
    try:
        skillset = AzureOpenAISkillset(
            search_endpoint,
            AzureKeyCredential(search_api_key),
            azure_ada_openai_config,
            index_name,
            skillset_name,
            analyzeDocumentAzureFunc_url,
            splitDocumentAzureFunc_url
        )
        skillset.create_skillset()
    except Exception as e:
        print(f"Error creating skillset: {e}")

    # Step 4: Create the indexer
    try:
        manager = AzureSearchIndexer(
            search_endpoint,
            AzureKeyCredential(search_api_key),
            index_name,
            skillset_name,
            data_source_name,
            indexer_name
        )
    except Exception as e:
        print(f"Error creating indexer: {e}")

    # Step 5: Run the indexer
    try:
        manager.create_indexer()
        manager.run_indexer()
    except Exception as e:
        print(f"Error running indexer: {e}")


# createAzureSearchItems(cases_index_name, cases_container_name)
# createAzureSearchItems(laws_index_name, laws_container_name)

createAzureSearchItems(index_name)