from dotenv.main import load_dotenv
from requests import get as rq_get
from unittest import TestCase, main as unit_main



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
        
        response = requests.post(f'{URL}/rfc-ph', json=w_missing['input'])
        self.assertEqual(response.status_code, 500)


if __name__ == '__main__': 
    import sys 
    from config import URLS, DEFAULT_ENV
    
    ENV = sys.argv.pop() if len(sys.argv) > 1 else DEFAULT_ENV
    URL = URLS[ENV]
    
    unit_main()


if False: 
    from importlib import reload
    from tests import test_rfc
    import config
    load_dotenv(override=True)
    reload(config)
    from config import URLS

    ENV = 'staging'  # 'qa' # 'staging' # 
    URL = config.URLS[ENV]

    test_run = test_rfc.RfcTestCase()
    example  = set_example()

    # headers  = {
    #     'grant_type': 'client_credentials',
    #     'client_id': _env(), 'client_secret' : '', 'scope' : ''}
    
    response = rq_get(f'{URL}/get-rfc', json=example['input'])    



