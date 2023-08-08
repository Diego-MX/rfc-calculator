import re
from operator import itemgetter
from datetime import datetime as dt
import pandas as pd
from fastapi import status, Response
from fastapi.exceptions import HTTPException

from src.utilities.basic import str_delatinize
from src.get_rfc import rfc_completo, PersonPhysical
from src.app.models import RFCValidationResponse



def process_rfc_physical(an_input): 
    try: 
        a_person   = an_input.get('personPhysical')
        campos_ls  = ['last_name', 'maternal_last_name', 'first_name']
        nombres_ls = itemgetter(*campos_ls)(a_person)
        f_inicio   = dt.strptime(a_person.get('date_of_birth'), '%Y-%m-%d')
        el_rfc     = rfc_completo('fisica', nombres_ls, f_inicio)
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


def validate_rfc_physical(req_validation, response:Response): 
    try:
        rfc_user = req_validation.userRFC
        rfc_engine = req_validation.calculatedRFC

        okay_keys = PersonPhysical.validate_rfc(rfc_user, rfc_engine)
        
        if all(okay_keys[:-1]):  # except last one. 
            index = -1
        elif okay_keys[-1]: 
            index = -4
        else:
            index = -2

        if index != -2: 
            return RFCValidationResponse.from_key(index)
        else: 
            response.status_code = status.HTTP_409_CONFLICT
            return response

    except Exception as expt: 
        raise HTTPException(status_code=500, detail=str(expt))


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
        
