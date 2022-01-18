from operator import itemgetter
from datetime import datetime as dt
from fastapi.exceptions import HTTPException

from flask import jsonify
from src.get_rfc import rfc_completo


def process_request(input, server="flask"): 
    try: 
        a_person     = input.get("personPhysical")
        campos_ls    = ["lastName", "maternalLastName", "firstName"]
        nombres_ls   = itemgetter(*campos_ls)(a_person)
        f_inicio     = dt.strptime(a_person.get("dateOfBirth"), "%Y-%m-%d")
        el_rfc       = rfc_completo("fisica", nombres_ls, f_inicio)
        la_respuesta = {"rfc" : el_rfc}
        estatus      = 200
    except Exception as exc: 
        la_respuesta = {
            "code"       : "0002",
            "status_code": "500",
            "type"       : "internal-error",
            "instance"   : "input/get-rfc/internal-error",
            "timestamp"  : str(dt.now()),
            "detail"     : str(exc)}
        estatus = 500

    if server == "flask":
        return (jsonify(la_respuesta), estatus)
    
    elif server == "fastapi": 
        try: 
            f_inicio = dt.strptime(a_person.get("dateOfBirth"), "%Y-%m-%d")
        except ValueError: 
            excepcion = HTTPException(status_code=400, 
                detail="dateOfBirth: Incorrect data format, use YYYY-MM-DD")
            raise excepcion
        return la_respuesta    
        # la_respuesta
        
    

