from flask import Flask, request

from src import engine 
from src.utilities import tools
import config

SITE = config.SITE
app  = Flask(__name__)


@app.route("/", methods=["GET"])
def base_url():
    return "Uploaded, version: 1.0.3"


# @app.route("/v1/validation-services/get-rfc", methods=["POST", "GET"])
# Las versiones se manejan en el API Management. 
@app.route("/get-rfc", methods=["POST", "GET"])
def get_rfc():
    an_input = request.json
    
    input_file   = SITE/"refs/openapi/1-rfc-input.json"
    a_validation = tools.response_validate(an_input, input_file)
    
    if a_validation["error"]:
        return a_validation["output"]
    
    b_response = engine.process_request(an_input)
    return b_response

       
# @app.route("/v1/validation-services/validate-rfc", methods=["POST", "GET"])
# def validate_rfc():
#     pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)



