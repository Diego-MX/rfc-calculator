import os
from pathlib import Path

SITE = Path(__file__).parent if "__file__" in globals() else Path(os.getcwd())

VERSION = "1.0.4"

URLS = {
    "local-flask"   : "http://localhost:5000/get-rfc", 
    "local-fastapi" : "http://localhost:80/rfc-pf", 
    "staging"       : "https://wap-validation-services-dev.azurewebsites.net/get-rfc",
    "qa"            : "https://apim-crosschannel-tech-dev.azure-api.net/data/validation-services/v1/get-rfc/"
}


DEFAULT_ENV = "staging"

