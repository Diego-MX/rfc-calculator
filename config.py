import os
from pathlib import Path

SITE = Path(__file__).parent if "__file__" in globals() else Path(os.getcwd())
DEFAULT_ENV = "staging"

URLS = {
    "local"     : "http://localhost:5000/get-rfc", 
    "staging"   : "https://wap-validation-services-dev.azurewebsites.net/get-rfc",
    "qa"        : "https://apim-crosschannel-tech-dev.azure-api.net/data/validation-services/v1/get-rfc/"
}




