import os
from azure.identity import ClientSecretCredential, DefaultAzureCredential

from config import ENV_KEYS, SITE
from dotenv import load_dotenv


class AzureResourcer(): 
    def __init__(self, env: str): 
        self.env = env

        if   env == "local":
            load_dotenv(SITE/".env", override=True)
            params = ENV_KEYS["platform"]["service-principal"]
            self.credential = ClientSecretCredential(**{ k: os.getenv(v) 
                for (k, v) in params.items() })        
        elif env == "managed":
            self.credential = DefaultAzureCredential()

        elif env == "databricks": 
            pass

        else: 
            raise "Azure Resourcer distinguishes LOCAL, MANAGED, DBKS environments."
    









