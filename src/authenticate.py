import os
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from config import SITE, ENV_KEYS
from dotenv import load_dotenv


class AzureResourcer(): 
    def __init__(self, env: str): 
        self.env    = env
        self.config = ENV_KEYS[env]
        self.set_credential()
        
    
    def set_credential(self): 
        if self.env == 'local': 
            load_dotenv(SITE/'.env', override=True)
            sp_keys = self.config['platform']['service-principal']
            self.credential = ClientSecretCredential(**{ k: os.getenv(v) 
                for (k, v) in sp_keys.items() })

        elif self.env in ['dev', 'qas']: 
            self.credential = DefaultAzureCredential()
        
        elif self.env == 'databricks': 
            pass
            
        else:
            raise 'Azure Resourcer distinguishes LOCAL, DEV, QAS, DBKS environments.'

    
    def get_blob_service(self): 
        blob_keys   = self.config['storage']
        the_service = BlobServiceClient(blob_keys['url'], self.credential)
        the_path    = blob_keys['root']
        return (the_service, the_path)







