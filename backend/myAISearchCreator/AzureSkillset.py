from azure.search.documents.indexes import SearchIndexerClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    SearchIndexerSkillset,
    SplitSkill,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    LanguageDetectionSkill
)


import os
from dotenv import load_dotenv

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
    
    # Not supported in Qatar Central
    # def create_language_detection_skill(self):

    #     return LanguageDetectionSkill(
    #         context="/document/pages/*",
    #         inputs=[
    #             InputFieldMappingEntry(name="text", source="/*"),
    #         ],
    #         outputs=[
    #             OutputFieldMappingEntry(name="languageCode", target_name="languageCode"),
    #             OutputFieldMappingEntry(name="languageName", target_name="languageName"),
    #         ],
    #     )

    
    # def create_metadata_skill(self):
    #     """
    #     Create a skill to generate metadata for chunks using GPT-4.
    #     """
    #     return AzureOpenAITextSkill(
    #         description="Generate metadata (summary, etc.) for each chunk using GPT-4",
    #         context="/document/pages/*",
    #         resource_uri=self.ada_openai_config['endpoint'],  # Azure OpenAI endpoint
    #         deployment_id="gpt-4o",  # Specify GPT-4 deployment
    #         model_name="gpt-4o",
    #         api_key=self.ada_openai_config['api_key'],
    #         inputs=[
    #             InputFieldMappingEntry(name="text", source="/document/pages/*"),
    #         ],
    #         outputs=[
    #             OutputFieldMappingEntry(name="summary", target_name="summary"),
    #             OutputFieldMappingEntry(name="metadata", target_name="metadata"),
    #         ],
    #         # Additional parameters like temperature, max tokens, or custom instructions can be set here
    #         parameters={
    #             "max_tokens": 300,
    #             "temperature": 0.7,
    #             "top_p": 1.0,
    #             "frequency_penalty": 0.0,
    #             "presence_penalty": 0.0,
    #         },
    #     )

    def create_embedding_skill(self):
        """
        Create an Azure OpenAI embedding skill.
        """
        return AzureOpenAIEmbeddingSkill(
            description="Skill to generate embeddings for chunks via Azure OpenAI",
            context="/document/pages/*",
            resource_url=self.ada_openai_config['endpoint'],
            deployment_name=self.ada_openai_config['deployment_id'],
            model_name=self.ada_openai_config['model_name'],
            dimensions=self.ada_openai_config['dimensions'],
            api_key=self.ada_openai_config['api_key'],
            inputs=[
                InputFieldMappingEntry(name="text", source="/document/pages/*"),
            ],
            outputs=[
                OutputFieldMappingEntry(name="embedding", target_name="vector"),
            ],
        )

    def create_skillset(self):
        """
        Create or update the skillset for the Azure Search index.
        """
        skills = [
            self.create_chunking_skill(),
            # self.create_language_detection_skill(),
            self.create_embedding_skill(),
        ]

        skillset = SearchIndexerSkillset(
            name=self.skillset_name,
            description="Skillset to chunk documents and generate embeddings",
            skills=skills,
            index_projection=SearchIndexerIndexProjection(
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
                            ),
                            # InputFieldMappingEntry(
                            #     name="languageCode",
                            #     source="/document/pages/*/languageCode"
                            # )
                            # ,
                            # InputFieldMappingEntry(
                            #     name="languageName",
                            #     source="/document/pages/*/languageName"
                            # )
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
