from dotenv import load_dotenv
import os

from openai import AzureOpenAI

class GPT_4o:
    def __init__(self):
        """
        Initialize the GPT_4o class by loading environment variables and setting up the AzureOpenAI client.
        """
        load_dotenv()
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

    def send_msg(self, system_msg: str, user_msg: str, max_tokens: int = 300):
        """
        Sends a test message to the Azure OpenAI GPT model and retrieves the response.

        Args:
            start_phrase (str): The user's message to the model.
            max_tokens (int): Maximum number of tokens for the response. Defaults to 50.

        Returns:
            str: The model's response content.
        """
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=max_tokens
        )

        return response.choices[0].message.content
    
    def summarize_text(self, text: str, max_tokens: int = 100):
        """
        Summarizes a given text using Azure OpenAI GPT-4.

        Args:
            text (str): The text to summarize.
            max_tokens (int): Maximum number of tokens for the response. Defaults to 100.

        Returns:
            str: The summarized text.
        """
        print('Sending a summarization request...')
        
        system_msg = "You are a helpful assistant that summarizes text for search indexing."
        user_msg = f"Summarize the following text:\n{text}"
        return self.send_msg(system_msg, user_msg, max_tokens)
