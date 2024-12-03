from azure.search.documents.indexes.models import (
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    SearchIndexerSkillset
)
from azure.search.documents.indexes import SearchIndexerClient
from azure.core.credentials import AzureKeyCredential

import os
from dotenv import load_dotenv

from azure.search.documents.indexes._generated.models import (
    SearchIndexerSkillset,
    SearchIndexerIndexProjections,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    InputFieldMappingEntry,
    OutputFieldMappingEntry
)

from azure.search.documents.indexes.models import (
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    SearchIndexerSkillset,
)

from azure.search.documents.indexes.models import (
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    SearchIndexerSkillset,
    SplitSkill
)

class AzureOpenAISkillset:
    def __init__(self, endpoint, credential, ada_openai_config, index_name, skillset_name):
        self.client = SearchIndexerClient(endpoint, credential)
        self.ada_openai_config = ada_openai_config
        self.index_name = index_name
        self.skillset_name = skillset_name

    def create_chunking_skill(self):
        """
        Create a skill to chunk documents.
        """
        return SplitSkill(
            description="Split documents into chunks",
            context="/document",
            inputs=[
                InputFieldMappingEntry(name="text", source="/document/content"),
            ],
            outputs=[
                OutputFieldMappingEntry(name="textItems", target_name="pages"),
            ],
            default_language_code="en",
            text_split_mode="pages",
            maximum_page_length=2000,
            page_overlap_length=500,
            # unit="characters"
        )

    def create_embedding_skill(self, description, context, input_source, output_target):
        """
        Create an Azure OpenAI embedding skill.
        """
        return AzureOpenAIEmbeddingSkill(
            description=description,
            context=context,
            resource_uri=self.ada_openai_config['endpoint'],
            deployment_id=self.ada_openai_config['deployment_id'],
            model_name=self.ada_openai_config['model_name'],
            dimensions=self.ada_openai_config['dimensions'],
            api_key=self.ada_openai_config['api_key'],
            inputs=[
                InputFieldMappingEntry(name="text", source=input_source),
            ],
            outputs=[
                OutputFieldMappingEntry(name="embedding", target_name=output_target),
            ],
        )

    def create_skillset(self):
        """
        Create or update the skillset for the Azure Search index.
        """
        skills = [
            self.create_chunking_skill(),
            self.create_embedding_skill(
                description="Skill to generate embeddings for chunks via Azure OpenAI",
                context="/document/pages/*",
                input_source="/document/pages/*",
                output_target="vector",
            ),
        ]

        skillset = SearchIndexerSkillset(
            name=self.skillset_name,
            description="Skillset to chunk documents and generate embeddings",
            skills=skills,
            index_projections=SearchIndexerIndexProjections(
                selectors=[
                    SearchIndexerIndexProjectionSelector(
                        target_index_name=self.index_name,
                        parent_key_field_name="parent_id",
                        source_context="/document/pages/*",
                        mappings=[
                            InputFieldMappingEntry(
                                name="chunk",
                                source="/document/pages/*"
                            ),
                            InputFieldMappingEntry(
                                name="vector",
                                source="/document/pages/*/vector"
                            ),
                            InputFieldMappingEntry(
                                name="title",
                                source="/document/title"
                            )
                        ]
                    )
                ],
                parameters=SearchIndexerIndexProjectionsParameters(projection_mode="skipIndexingParentDocuments")
            )
        )

        result = self.client.create_or_update_skillset(skillset)
        print(f"Skillset '{result.name}' created or updated successfully.")
        return result

# Example usage
if __name__ == "__main__":
    load_dotenv()
    # Replace these with actual values
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    azure_ada_openai_config = {
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "deployment_id": "text-embedding-ada-002",
        "model_name": "text-embedding-ada-002",
        "dimensions": 1536,
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
    }
    index_name = "law2006"
    skillset_name = f"{index_name}-skillset"

    manager = AzureOpenAISkillset(
        endpoint,
        AzureKeyCredential(api_key),
        azure_ada_openai_config,
        index_name,
        skillset_name
    )
    
    manager.create_skillset()
