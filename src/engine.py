from operator import itemgetter
from datetime import datetime as dt

from flask import jsonify
from src.get_rfc import rfc_completo


def process_request(input): 
    a_person = input.get("personPhysical")
    try: 
        campos_ls  = ["lastName", "maternalLastName", "firstName"]
        nombres_ls = itemgetter(*campos_ls)(a_person)
        f_inicio   = dt.strptime(a_person.get("dateOfBirth"), "%Y-%m-%d") 
        
        el_rfc       = rfc_completo("fisica", nombres_ls, f_inicio)
        la_respuesta = { "rfc" : el_rfc }
        
        return (jsonify(la_respuesta), 200)

    except Exception as exc:
        an_error = {
            "code"          : "0002",
            "status_code"   : "500",
            "type"          : "internal-error",
            "instance"      : "input/get-rfc/internal-error",
            "timestamp"     : str(dt.now()),
            "detail"        : str(exc)
        }
        return (jsonify(an_error), 500)
