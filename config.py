import os
from pathlib import Path

SITE = Path(__file__).parent if "__file__" in globals() else Path(os.getcwd())

ENV      = "managed"
VERSION  = "1.0.6"


URLS = {
    "local-flask"   : "http://localhost:5000/get-rfc", 
    "local-fastapi" : "http://localhost:80/rfc-pf", 
    "staging"       : "https://wap-validation-services-dev.azurewebsites.net/get-rfc",
    "qa"            : "https://apim-crosschannel-tech-dev.azure-api.net/data/validation-services/v1/get-rfc/"
}

ENV_KEYS = {
    "platform" : {
        "service-principal" : {
            "client_id"       : "SP_APP_ID", 
            "client_secret"   : "SP_APP_SECRET", 
            "tenant_id"       : "AZ_TENANT", 
            "subscription_id" : "AZ_SUBSCRIPTION" }, 
        "storage"   : {
            "name"  : "lakehylia", 
            "url"   : "https://lakehylia.blob.core.windows.net/", 
            "root"  : "product/epic-catalogs/app-services" }, 
} }

PATH_DIRS = {
    "managed" : Path("/temp"), 
    "local"   : SITE/"refs/temp", 
}

DEFAULT_ENV = "staging"



