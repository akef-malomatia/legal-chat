from pydantic import BaseModel
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from myOpenAI import AdaModel
from azure.search.documents.models import VectorQuery
from typing import List
from azure.search.documents.models import VectorizableTextQuery
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType
import logging
from azure.cosmos import CosmosClient

from myOpenAI import GPT_4o
import os
from dotenv import load_dotenv

class QueryRequest(BaseModel):
    query: str

class LegalAssistant:
    
    def __init__(self):
        load_dotenv()

        # Cosmos DB details
        cosmos_endpoint = os.getenv("COSMOS_DB_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_DB_PRIMARY_KEY")
        database_name = "config-database"
        container_name = "config-container"

        # Initialize Cosmos client and fetch the configuration
        client = CosmosClient(cosmos_endpoint, cosmos_key)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        # Fetch configuration document by "rg-ai01"
        config_item = container.read_item(item="rg-ai01", partition_key="rg-ai01")

        # Extract values from the configuration document
        search_endpoint = config_item["ai_search"]["endpoint"]
        search_api_key = config_item["ai_search"]["api_key"]
        self.cases_index_name = config_item["ai_search"]["cases_index_name"]
        self.laws_index_name = config_item["ai_search"]["laws_index_name"]
        self.auzre_openai_endpoint = config_item["openai_malomatia"]["endpoint"]
        self.azure_openai_api_key = config_item["openai_malomatia"]["api_key"]
        self.ada_version = config_item["openai_malomatia"]["ada_version"]
        self.gpt_version = config_item["openai_malomatia"]["version"]
        self.gpt_deployment_name = config_item["openai_malomatia"]["deployment_name"]

        # Initialize Azure Search Client
        self.case_search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=self.cases_index_name,
            credential=AzureKeyCredential(search_api_key)
        )
        
        self.law_search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=self.laws_index_name,
            credential=AzureKeyCredential(search_api_key)
        )

    def encode_query_to_vector(self, query: str) -> List[VectorQuery]:
        ada_model = AdaModel(self.azure_openai_api_key, self.ada_version, self.auzre_openai_endpoint)

        # Encode a single query
        query = "What are the laws regarding business registration in Qatar?"
        vector = ada_model.encode(query)

        return vector

    def get_case_sources(self, query):
        if query is None:
            raise ValueError("Query cannot be None") 
        # vector_queries = VectorizedQuery(kind="vector", k_nearest_neighbors=50, vector=self.encode_query_to_vector(query), fields="content_vector")
        vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=50, fields="content_vector")

        try:
            case_sources = []
            search_results = self.case_search_client.search(  
                search_text=query,  
                vector_queries=[vector_query],
                select=["title", "page_number", "page_content"],
                query_type=QueryType.SEMANTIC,
                semantic_configuration_name=f'{self.cases_index_name}-semantic-config',
                # query_rewrites="generative|count-5",
                # query_language="en",
                # debug=QueryDebugMode.QUERY_REWRITES,
                query_caption=QueryCaptionType.EXTRACTIVE,
                query_answer=QueryAnswerType.EXTRACTIVE,
                top=3
            )
            
            for document in search_results:
                case = {
                    "title": document["title"],
                    "page_number": document["page_number"],
                    "page_content": document["page_content"],
                    "@search.score": document["@search.score"]
                }
                case_sources.append(case)
        except Exception as e:
            logging.error(f"Error retrieving case search results: {str(e)}")

        return case_sources
    
    def get_law_source(self, case_sources: List[dict]) -> List[dict]:
        if case_sources is None:
            raise ValueError("Case sources cannot be None")
        
        law_sources = []
        for document in case_sources:
            vector_query = VectorizableTextQuery(text=document["page_content"], k_nearest_neighbors=50, fields="content_vector")

            try:
                search_results = self.law_search_client.search(  
                    search_text=document["page_content"],  
                    vector_queries=[vector_query],
                    select=["title", "page_number", "page_content"],
                    query_type=QueryType.SEMANTIC,
                    semantic_configuration_name=f'{self.laws_index_name}-semantic-config',
                    # query_rewrites="generative|count-5",
                    # query_language="en",
                    # debug=QueryDebugMode.QUERY_REWRITES,
                    query_caption=QueryCaptionType.EXTRACTIVE,
                    query_answer=QueryAnswerType.EXTRACTIVE,
                    top=3
                )
                
                if search_results:
                    law_sources.extend(search_results)
            except Exception as e:
                logging.error(f"Error retrieving case search results: {str(e)}")
            
            break;    
        
        return law_sources
    
    def format_sources(self, sources: List[dict]) -> str:
        try:
            return "\n".join([
                f'{document["title"]}:{document["page_number"]}:{document["page_content"]}:{document["@search.score"]}' for document in sources
            ])
        except Exception as e:
            logging.error(f"Error formating search results: {str(e)}")

    # def print_results(self, results: SearchItemPaged[dict]):
    #     semantic_answers = results.get_answers()
    #     if semantic_answers:
    #         for answer in semantic_answers:
    #             if answer.highlights:
    #                 print(f"Semantic Answer: {answer.highlights}")
    #             else:
    #                 print(f"Semantic Answer: {answer.text}")
    #             print(f"Semantic Answer Score: {answer.score}\n")

    #     for result in results:
    #         print(f"Title: {result['title']}")  
    #         print(f"Score: {result['@search.score']}")
    #         if result.get('@search.reranker_score'):
    #             print(f"Reranker Score: {result['@search.reranker_score']}")
    #         print(f"Content: {result['page_content']}")  

    def get_legal_answer(self, request: QueryRequest):
        gpt_4o = GPT_4o(self.azure_openai_api_key, self.gpt_version, self.auzre_openai_endpoint, self.gpt_deployment_name)
        
        print(f"Request query: {request.query}")
        
         # Define the grounded prompt template
        grounded_prompt = """
                You are a friendly assistant providing legal information based on Qatari laws.
                Answer the inquiry using only the sources listed below in a professional and concise manner.
                Only provide the information listed in the source list below.
                If there is not enough information below, state that you do not know.
                If you do not find the law related to the inquiry, state: "I did not find the law related to the inquiry."
                Do not generate answers that are not based on the sources below.
                Inquiry: {query}
                Case Source: {case_sources}
                Legal Source: {law_sources}
            """


        system_msg = "You are a Qatari Judge"
        case_sources = self.get_case_sources(request.query)
        law_sources = self.get_law_source(case_sources)
        # print(f"Law sources: {law_sources}")
        
        try: 
            formated_case_sources = self.format_sources(case_sources)
            formated_law_sources = self.format_sources(law_sources)
            user_msg = grounded_prompt.format(
                    query=request.query, 
                    case_sources=formated_case_sources, 
                    law_sources=formated_law_sources
                )
            
            grounded_prompt_reponse_format = """
            Please format the answer as follows:
                {
                    "answer": [answer here],
                    "case_source": [source name here],
                    "case_page_number": [case page number here],
                    "legal_text": [legal text here],
                    "legal_source": [legal source name here],
                    "legal_source_page_number": [legal source page number here]
                }
                
                Example of a question and how to answer:
                Question: What was the judgment for the plaintiff Marah Ghazali?

                If the information is available:
                {
                   "answer": "The court ruled in favor of the plaintiff Marah Ghazali with compensation of 50,000 Qatari Riyals for damages resulting from breach of contract according to Article 105 of the Qatari Civil Code.",
                   "case_source": "Marah Ghazali vs. Al-Amal Company.",
                   "case_page_number": 45,
                   "legal_text": "Arbitrary dismissal, which does not allow the first party to arbitrarily terminate the contract without the consent of the second party.",
                   "legal_source": "Qatari Civil Code.",
                   "legal_source_page_number": 23
                }
                

                If the information is not available:
                {
                    "answer": "I did not find the case related to the inquiry.",
                    "case_source": "Relevant information not found.",
                    "case_page_number": "Not available.",
                    "legal_text": "Relevant information not found.",
                    "legal_source": "Not available.",
                }
                
                DONNOT MIX BETWEEN CASES AND LAWS.
                LEGAL TEXT MUST BE FROM Legal Source.
                
                Reply in ARABIC a json format.
            """
        except Exception as e:
            logging.error(f"Error formatting the grounded prompt: {str(e)}")
            results = {
                "response": "Server Error",
                "sources_formatted": case_sources,
                "user_msg": user_msg
            }

        try:
            response = gpt_4o.send_msg(system_msg, user_msg + grounded_prompt_reponse_format)
            
            print(response)
            
            results = {
                "response": response,
                "sources_formatted": case_sources,
                "user_msg": user_msg
            }
        except Exception as e:
            # Check for 429 error code (rate limit exceeded)
            if '429' in str(e):
                logging.error("Rate limit exceeded: Please retry after 86400 seconds. You can increase your token limit at https://aka.ms/oai/quotaincrease")
                results = {
                    "response": "Rate limit exceeded. Please retry later.",
                    "sources_formatted": case_sources,
                    "user_msg": user_msg
                }
            else:
                logging.error(f"Error generating response: {str(e)}")
                results = {
                    "response": "Server Error",
                    "sources_formatted": case_sources,
                    "user_msg": user_msg
                }

        return results
