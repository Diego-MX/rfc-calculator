import requests
from unittest import TestCase, main as unit_main

class RfcTestCase(TestCase):
    def set_example(self): 
        an_example = {
            "input" : { 
                "personPhysical" : { 
                    "firstName"         : "Diego", 
                    "lastName"          : "Villamil", 
                    "maternalLastName"  : "Pesqueira", 
                    "dateOfBirth"       : "1983-12-27"} }, 
            "output"    : {
                "rfc"   : "VIPD831227DH2"} }
        return an_example


    def test_correct_usage(self):
        myself = self.set_example()

        response = requests.post(URL, json=myself["input"])
        obtained = response.json()
        self.assertDictEqual(obtained, myself["output"])


    def later_test_missing_arguments_returns_500(self):
        w_missing = self.set_example()
        w_missing["input"]["personPhysical"].pop("firstName")
        
        response = requests.post(URL, json=w_missing["input"])
        self.assertEqual(response.status_code, 500)


if __name__ == "__main__": 
    import sys 
    import config
    
    ENV = sys.argv.pop() if len(sys.argv) > 1 else config.DEFAULT_ENV
    URL = config.ENV_URLS[ENV]

    unit_main()

if False: 
    from importlib import reload
    from tests import test_rfc
    import config
    

    ENV = "local"  # "staging"
    URL = config.ENV_URLS[ENV]

    test_run = test_rfc.RfcTestCase()
    example  = test_run.set_example()
    response = requests.post(URL, json=example["input"])    



