from datetime import datetime as dt
from jsonschema.exceptions import ValidationError
from flask import Flask, request, jsonify
from operator import itemgetter

from src.utilities.tools import validate_input
from src.utilities.get_rfc import rfc_completo

app = Flask(__name__)


@app.route("v1/validation-services/validate-rfc", methods=["POST", "GET"])
def validate_rfc():
    pass


@app.route("v1/validation-services/get-rfc", methods=["POST", "GET"])
def get_rfc():
    
    an_input = request.json
    try:
        validate_input(an_input)
    except ValidationError as e:
        # invalid input
        response = {
            "code"          : "0001",
            "type"          : "validation/input",
            "status_code"   : "400",
            "timestamp"     : str(dt.now()),
            "instance"      : "input/pricing_model/invalid_structure",
            "detail"        : str(e)
        }
        return (jsonify(response), 400)

    a_person = an_input.get("personPhysical")
    try: 
        campos_ls  = ["lastName", "maternalLastName", "firstName"]
        nombres_ls = itemgetter(campos_ls)(a_person)
        f_inicio   = dt.strptime(a_person.get("dateOfBirth"), "%Y-%m-%d") 
        
        el_rfc       = rfc_completo("fisica", nombres_ls, f_inicio)
        la_respuesta = { "rfc" : el_rfc }
        return (jsonify(la_respuesta), 200)

    except Exception as e:
        an_error = {
            "code"          : "0002",
            "type"          : "internal-error",
            "status_code"   : "500",
            "timestamp"     : str(dt.now()),
            "instance"      : "input/get-rfc/internal-error",
            "detail"        : str(e)
        }
        return (jsonify(an_error), 500)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0")



