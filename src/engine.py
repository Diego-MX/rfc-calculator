from email.policy import HTTP
import re
from operator import itemgetter
from datetime import datetime as dt
import pandas as pd
from fastapi.exceptions import HTTPException

from src.utilities.basic import str_delatinize
from src.get_rfc import rfc_completo, PersonPhysical
from src.app.models import InvalidRFCResponse

#%% Some helper functions

def first_true(a_list:list, from_end=False): 
    b_list = a_list.copy()
    if from_end: 
        b_list = b_list.reverse()
    trues = [ii for x, ii in enumerate(a_list) if x]
    a_first = trues[0] if trues else None
    return a_first


#%% The calls. 

def process_rfc_physical(an_input): 
    try: 
        a_person     = an_input.get('personPhysical')
        campos_ls    = ['last_name', 'maternal_last_name', 'first_name']
        nombres_ls   = itemgetter(*campos_ls)(a_person)
        f_inicio     = dt.strptime(a_person.get('date_of_birth'), '%Y-%m-%d')
        el_rfc       = rfc_completo('fisica', nombres_ls, f_inicio)
        return {'rfc' : el_rfc}

    except ValueError: 
        the_exception = HTTPException(status_code=400, 
                detail="dateOfBirth: Incorrect data fromat, use YYYY-MM-DD")
        raise the_exception
    except Exception as expt: 
        raise HTTPException(status_code=500, detail=str(expt))


def process_rfc_physical_2(person): 
    try: 
        the_rfc = person.get_rfc()
        return {'rfc' : the_rfc}
    except ValueError: 
        the_exception = HTTPException(status_code=400, 
                detail="dateOfBirth: Incorrect data fromat, use YYYY-MM-DD")
        raise the_exception
    except Exception as expt: 
        raise HTTPException(status_code=500, detail=str(expt))


def validate_rfc_physical(rfc_user, rfc_engine): 
    try: 
        fail_keys = [not ok for ok in PersonPhysical.validate_rfc(rfc_user, rfc_engine)]

        if sum(fail_keys) == 0: 
            an_obj = InvalidRFCResponse.from_key(-1)
            status = 200
        elif sum(fail_keys) == 1:
            an_obj = InvalidRFCResponse.from_key(fail_keys[0])
            status = 409
        elif sum(fail_keys) > 1:
            an_obj = InvalidRFCResponse.from_key(-2)
            status = 409
    except Exception as expt: 
        raise HTTPException(status_code=500, detail=str(expt))
    
    if status == 200: 
        return an_obj
    else: 
        raise HTTPException(status, an_obj.json())


def process_curp(person_obj: PersonPhysical):
    try:
        the_curp = person_obj.get_curp()
        return {'curp': the_curp}
    except AttributeError: 
        raise HTTPException(status_code=500, 
            detail='Must include stateOfBirth, gender.')
    except Exception as expt: 
        raise HTTPException(status_code=500, detail=str(expt))


def approve_alias(an_alias): 
    try: 
        offensive_df  = pd.read_feather('refs/temp/offensive-words.feather').dropna()
        offensive_srs = offensive_df['Phrase'].str.lower().apply(str_delatinize)

        offensive_str_2 = '|'.join(offensive_srs.tolist())
        offensive_str_1 = re.sub(r' ?\((.*?)\)', r'|\1', offensive_str_2)
        offensive_str   = rf'({(offensive_str_1)})'
        
        is_offensive = re.search(offensive_str, an_alias, re.IGNORECASE)

        response = {'alias': an_alias}
        if is_offensive:
            offense = is_offensive.group(0).lower()
            indices = offensive_srs.str.contains(offense)
            which_offensive = offensive_df.loc[indices, 'Type'].tolist()[0]
            response.update({
                'offense'     : offense, 
                'offenseType' : which_offensive}) 
        return response

    except Exception as expt: 
        raise HTTPException(status_code=500, detail=str(expt))
        
