import requests
from unittest import TestCase, main as unit_main

URL = "http://localhost:5000/v1/validation-services/get-rfc"
# URL = "https://wap-validation-services-dev.azurewebsites.net/v1/validation-services/get-rfc"


class RfcTestCase(TestCase):

    def test_correct_usage(self):
        myself = {
            "input" : { "personPhysical" : { 
                "firstName"         : "Diego", 
                "lastName"          : "Villamil", 
                "maternalLastName"  : "Pesqueira", 
                "dateOfBirth"       : "1983-12-27"}}, 
            "output"    : {
                "rfc"   : "VIPD831227DH2"} }

        response = requests.post(URL, json=myself["input"])
        obtained = response.json()
        self.assertEqual(obtained, myself["output"])

    def test_missing_arguments(self):
        w_missing = { "input" : { "personPhysical" : {
            "lastName"          : "Villamil", 
            "maternalLastName"  : "Pesqueira", 
            "dateOfBirth"       : "1983-12-27"
            } }, 
            "output" : { "error" : "An Error" } 
        }
        
        response = requests.post(URL, json=w_missing["input"])
        self.assertEqual(response)



if __name__ == "__main__": 
    unit_main()

