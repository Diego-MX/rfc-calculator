import os
from pathlib import Path

SITE = Path(__file__).parent if '__file__' in globals() else Path(os.getcwd())

ENV      = os.getenv('ENV', 'local')  # 'local', 'dev', 'qas', 'databricks'
VERSION  = '1.0.21'


# Estos son los endpoints finales para hacer pruebas. 
URLS = {
    'local'   : 'http://localhost:80', 
    'staging' : 'https://wap-validation-services-dev.azurewebsites.net',
    'qa'      : 'https://apim-crosschannel-tech-dev.azure-api.net/data/validation-services/v1'
}

ENV_KEYS = {
    'local' : {
        'service-principal' : {
            'client_id'       : 'SP_APP_ID', 
            'client_secret'   : 'SP_APP_SECRET', 
            'tenant_id'       : 'AZ_TENANT', 
            'subscription_id' : 'AZ_SUBSCRIPTION' }, 
        'storage'   : {
            'name'  : 'lakehylia', 
            'url'   : 'https://lakehylia.blob.core.windows.net/', 
            'root'  : 'product/epic-catalogs/app-services' 
    }   }, 
    'dev'   : {
        'storage'   : {
            'name'  : 'lakehylia', 
            'url'   : 'https://lakehylia.blob.core.windows.net/', 
            'root'  : 'product/epic-catalogs/app-services' 
    }   }, 
    'qas'   : {
        'storage'   : {
            'name'  : 'stlakehyliaqas', 
            'url'   : 'https://stlakehyliaqas.blob.core.windows.net/', 
            'root'  : 'product/epic-catalogs/app-services' }
} } 


# Se utiliza para guardar archivos temporales, dependiendo del ambiente. 
PATH_DIRS = {
    'local' : SITE/'refs/temp', 
    'dev'   : Path('/tmp'), 
    'qas'   : Path('/tmp')
    
}

# Este se usa para correr tests. 
DEFAULT_ENV = 'dev'



