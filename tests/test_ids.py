from unittest import TestCase, main as unit_main

from requests import get as rq_get, post


def set_example(type=None): 
    
    if (type is None) or (type == 'simple'):
        an_example = {
            'input' : { 
                'personPhysical' : { 
                    'firstName'         : 'Diego', 
                    'lastName'          : 'Villamil', 
                    'maternalLastName'  : 'Pesqueira', 
                    'dateOfBirth'       : '1983-12-27'} }, 
            'output'    : {
                'rfc'   : 'VIPD831227DH2'} }
    return an_example


class RfcTestCase(TestCase):
    
    def test_correct_usage(self):
        myself   = set_example()
        response = rq_get(f'{URL}/get-rfc', json=myself['input'])
        obtained = response.json()
        self.assertDictEqual(obtained, myself['output'])

    
    
    def need_test_to_check_wrong_date_format(self): 
        pass

    def later_test_missing_arguments_returns_500(self):
        w_missing = set_example()
        w_missing['input']['personPhysical'].pop('firstName')
        
        response = post(f'{URL}/rfc-ph', json=w_missing['input'])
        self.assertEqual(response.status_code, 500)


if __name__ == '__main__': 
    import sys 
    from config import URLS, DEFAULT_ENV
    
    ENV = sys.argv.pop() if len(sys.argv) > 1 else DEFAULT_ENV
    URL = URLS[ENV]
    
    unit_main()


if False: 
    from src import engine
    import requests
    from importlib import reload
    from tests import test_ids
    import config
    reload(config)
    from config import URLS
    from src.app.models import RequestValidation

    ENV = 'local'  # 'qa' # 'staging' # 
    URL = config.URLS[ENV]

    example  = set_example()

    person_dict = {
        'firstName': 'Diego', 'lastName': 'Villamil', 'maternalLastName': 'Pesqueira', 
        'dateOfBirth': '1983-12-27'
    }
    abc = requests.post(f'{URL}/rfc-ph', json=person_dict)

    validate_dict = {'userRFC': 'VIPC831227DH3', 'calculatedRFC': 'VIPD831227DH2'}

    abc = requests.post(f'{URL}/rfc-validate', json=validate_dict)
    req_validation = RequestValidation(**validate_dict)
    (rfc_user, rfc_engine) = (req_validation.userRFC, req_validation.calculatedRFC)
    efg = engine.validate_rfc_physical(rfc_user, rfc_engine)