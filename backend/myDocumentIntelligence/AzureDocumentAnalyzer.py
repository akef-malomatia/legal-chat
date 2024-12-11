import os
from dotenv import load_dotenv

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import AnalyzeResult

class AzureDocumentAnalyzer:

    def __init__(self, endpoint: str, credential):
        self.client = DocumentIntelligenceClient(endpoint, credential)

    def analyze_doc(self, file_path):
        """
        Analyzes a local document using the prebuilt-layout model.
        """
        with open(file_path, "rb") as file_stream:
            poller = self.client.begin_analyze_document(
                "prebuilt-layout", analyze_request=file_stream, content_type="application/octet-stream"
            )
            result = poller.result()

        # Process and print the results
        for page in result.pages:
            print(f"Page number: {page.page_number}")
            print(f"Text content:")
            for line in page.lines:
                print(line.content)
        print("Analysis complete.")

# Example usage of the class
if __name__ == "__main__":
    load_dotenv()
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    credential = AzureKeyCredential(os.getenv("AZURE_DOCUMENT_INTELLIGENCE_API_KEY"))

    file_name = "LAW NO. 22 of 2006 PROMULGATING 'THE FAMILY LAW'.doc"
    file_path = os.path.join("..", "..", "..", "..", "Data Source", file_name)

    # Create the index
    law_index = AzureDocumentAnalyzer(endpoint, credential)
    law_index.analyze_doc(file_path)
