import sys
from fastapi import FastAPI, Response
from json import loads
import uvicorn


from .models import (RequestValidation, RequestRFC, 
        OffensiveResponse, RFCValidationResponse, ORJSONResponse)
from src.get_rfc import PersonPhysical
from src import engine
from config import VERSION


app = FastAPI(
    title="Service Validation", 
    version=VERSION,
    openapi_tags=[
        {'name': 'ID keys', 
            'description': "Obtain RFC and CURP for Persons (Physical); use date format YYYY-MM-DD."}, 
        {'name': 'Alias', 'description': "Verify an alias doesn't contain offensive or curse words."}, 
        {'name': 'Base', 'description': "Check base endpoint and version."}, 
        {'name': 'Legacy'}], 
    root_path="data/docs/v1/validation-services",
    default_response_class=ORJSONResponse)


@app.get("/", tags=['Base'])
async def root():
    return f"Uploaded, version: {VERSION}"


# Este es el bueno. 
@app.post("/curp", tags=['ID keys'])
async def person_curp(req_person: PersonPhysical):    
    return engine.process_curp(req_person)



@app.post("/rfc-ph", tags=['ID keys'])
async def person_physical_rfc(req_person: PersonPhysical):    
    return engine.process_rfc_physical_2(req_person)


@app.post("/rfc-validate", tags=['ID keys'], 
        response_model=RFCValidationResponse)
async def validate_rfc_physical(req_validation: RequestValidation, response: Response):
    return engine.validate_rfc_physical(req_validation, response)


@app.get("/approve-alias/{alias}", tags=['Alias'], 
        response_model=OffensiveResponse)
async def alias_approval(alias: str): 
    a_response = engine.approve_alias(alias)
    return a_response


@app.get("/get-rfc", tags=['Legacy'])
async def rfc_get(a_request: RequestRFC):    
    an_input = loads(a_request.json())
    a_response = engine.process_rfc_physical(an_input)
    return a_response


@app.post("/get-rfc", tags=['Legacy'])
async def rfc_post(a_request: RequestRFC):    
    an_input = loads(a_request.json())
    a_response = engine.process_rfc_physical(an_input)
    return a_response
    


if __name__ == '__main__': 
    if 'debug' in sys.argv: 
        uvicorn.run("__main__:app", port=80, host="0.0.0.0", reload=True)
    else:
        uvicorn.run(app, port=80, host="0.0.0.0")


