import requests

URL = "https://wap-validation-services-dev.azurewebsites.net/rfc"

johnny = {
    "personPhysical" : {
        "firstName"         : "Diego", 
        "lastName"          : "Villamil", 
        "maternalLastName"  : "Pesqueira", 
        "dateOfBirth"       : "1983-12-27"
    }
}

response = requests.post(URL, json=johnny)
print(response.json())