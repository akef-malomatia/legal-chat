from azure.storage.blob import BlobClient, ContainerClient

from dotenv import load_dotenv
import os
import logging

class AzureBlobUploader:
    def __init__(self, sas_url):
        """
        Initializes the AzureBlobUploader class with the provided SAS URL.
        """
        load_dotenv()
        self.sas_url = sas_url
        self.container_client = ContainerClient.from_container_url(self.sas_url)

    def upload_file(self, local_file_path: str, blob_name: str):
        """
        Uploads a file to Azure Blob Storage using the SAS URL.
        
        :param local_file_path: The path to the local file to be uploaded.
        :param blob_name: The name to be given to the file in the Azure container.
        """
        try:
            # Construct the full blob URL by appending the blob name to the SAS URL
            blob_url = f"{self.sas_url.split('?')[0]}/{blob_name}?{self.sas_url.split('?')[1]}"

            # Create a BlobClient for the specific blob
            blob_client = BlobClient.from_blob_url(blob_url)

            # Upload the file to blob storage
            with open(local_file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)  # Overwrite if the file exists
            print(f"File '{local_file_path}' uploaded to blob storage as '{blob_name}'.")
        except Exception as e:
            logging.error(f"Error uploading file: {str(e)}")  # Replace print with logging

# Example usage
if __name__ == "__main__":
    uploader = AzureBlobUploader()
    file_name = "LAW NO. 22 of 2006 PROMULGATING 'THE FAMILY LAW'.doc"
    file_path = os.path.join("..", "..", "..", "Data Source", file_name)
    print(file_path)
    uploader.upload_file(file_path, file_name)
