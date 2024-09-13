from datetime import datetime as dt
from operator import itemgetter
import re
from typing import Tuple

from fastapi import status, Response
from fastapi.exceptions import HTTPException
import numpy as np
import pandas as pd

from src.utilities.basic import str_delatinize, thread
from src.get_rfc import rfc_completo, PersonPhysical
from src.app.models import RFCValidationResponse
from src.app.exceptions import FormatError
from src.app.alias import leet_1337

def process_rfc_physical_2(person: PersonPhysical): 
    the_rfc = person.get_rfc()
    return {'rfc' : the_rfc}


def validate_rfc_physical(req_validation, response: Response): 
    rfc_user = req_validation.userRFC
    rfc_engine = req_validation.calculatedRFC
    okay_keys = PersonPhysical.validate_rfc(rfc_user, rfc_engine)
    if all(okay_keys[:-1]):
        index = -1
    elif okay_keys[-1]: 
        index = -4
    else:
        index = -2
        response.status_code = status.HTTP_409_CONFLICT
        return response
    return RFCValidationResponse.from_key(index)        


def process_curp(person_obj:PersonPhysical):
    the_curp = person_obj.get_curp()
    return {'curp': the_curp}


def process_rfc_physical(an_input):
    a_person   = an_input.get('personPhysical')
    campos_ls  = ['last_name', 'maternal_last_name', 'first_name']
    nombres_ls = itemgetter(*campos_ls)(a_person)
    f_inicio   = dt.strptime(a_person.get('date_of_birth'), '%Y-%m-%d')
    el_rfc     = rfc_completo('fisica', nombres_ls, f_inicio)
    return {'rfc' : el_rfc}
