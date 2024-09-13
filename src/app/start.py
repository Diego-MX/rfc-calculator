
from collections import namedtuple
import sys

from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse
import uvicorn

from src import engine
from src.get_rfc import PersonPhysical
from src.app.alias import leet_1337 as leet
from config import VERSION

from .models import (RequestValidation, RequestRFC, 
    OffensiveResponse, RFCValidationResponse, ORJSONResponse)
from .exceptions import ValidationError

debug = 'debug' in sys.argv
root_path = "data/docs/v1/validation-services" if not debug else None

app_tags = {
    'ID keys': ("Obtain RFC and CURP for Persons (Physical);" 
            "use date format YYYY-MM-DD."), 
    'Alias' : "Verify an alias doesn't contain offensive or curse words.", 
    'Base'  : "Check base endpoint and version.", 
    'Legacy': "Old endpoints"}

Tag = namedtuple('Tag', ['name', 'description'])
tag_item = lambda nn_dd: Tag(*nn_dd)._asdict

app = FastAPI(
    title="Service Validation",
    version=VERSION,
    openapi_tags=list(map(tag_item, app_tags.items())), 
    root_path=root_path,
    default_response_class=ORJSONResponse)

@app.exception_handler(ValidationError)
async def catalogs_exception_handler(_:Request, exc:ValidationError):
    exc_code = ValidationError.mapping.get(type(exc), 500)
    exc_response = JSONResponse(
        status_code=exc_code,
        content={"message": f"{exc.name}: {exc.detail}"})
    return exc_response


@app.get("/", tags=['Base'])
async def root():
    return f"Uploaded, version: {VERSION}"


# Este es el bueno. 
@app.post("/curp", tags=['ID keys'])
async def person_curp(req_person:PersonPhysical):    
    return engine.process_curp(req_person)


@app.post("/rfc-ph", tags=['ID keys'])
async def person_physical_rfc(req_person:PersonPhysical):    
    return engine.process_rfc_physical_2(req_person)


@app.post("/rfc-validate", tags=['ID keys'])
async def validate_rfc_physical(
    req_val:RequestValidation, response:Response
    ) -> RFCValidationResponse:
    return engine.validate_rfc_physical(req_val, response)


@app.get("/approve-alias/{alias}", tags=['Alias'])
async def alias_approval(alias:str) -> OffensiveResponse: 
    return leet.offensive_alias(alias)


#%% A partir de aquí son Legacy. 

@app.get("/get-rfc", tags=['Legacy'])
async def rfc_get(a_request:RequestRFC):    
    a_response = engine.process_rfc_physical_2(a_request.personPhysical)
    return a_response


@app.post("/get-rfc", tags=['Legacy'])
async def rfc_post(a_request:RequestRFC):    
    a_response = engine.process_rfc_physical_2(a_request.personPhysical)
    return a_response
    


if __name__ == '__main__': 
    if 'debug' in sys.argv: 
        uvicorn.run("__main__:app", port=80, host="0.0.0.0", reload=True)
    else:
        uvicorn.run(app, port=80, host="0.0.0.0")
