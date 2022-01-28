# Conversión de Flask a FastAPI y uvicorn.
# TODO: Better error handling with dates and errors raised.
import sys
from fastapi import FastAPI
from json import loads
import uvicorn

from .models import ORJSONResponse, RequestRFC, OffensiveResponse
from src import engine
from config import VERSION

debug = ("debug" in sys.argv)

app = FastAPI(title="Validación de servicios", version=VERSION,
    openapi_tags=[
        { "name": "RFC", 
            "description": "Calcula el RFC para Personas Físicas. El formato de fecha de nacimiento YYYY-DD-MM." }, 
        { "name": "Alias", "description": "Verifica que un alias no tenga palabras altisonantes u ofensivas." }, 
        { "name": "Base", "description": "Check base endpoint and version" }, 
        { "name": "Legacy" }], 
    root_path="data/docs/v1/validation-services",
    default_response_class=ORJSONResponse)

@app.get("/", tags=["Base"])
async def root():
    return f"Uploaded, version: {VERSION}"


# Este es el bueno. 
@app.get("/rfc-pf", tags=["RFC"])
async def person_physical(a_request: RequestRFC):    
    an_input   = loads(a_request.json())    
    a_response = engine.process_rfc_physical(an_input)
    return a_response


# Estos dos se habían compartido y se quedan para compatibilidad. 
@app.get("/get-rfc", tags=["Legacy"])
async def rfc_get(a_request: RequestRFC):    
    an_input = loads(a_request.json())
    a_response = engine.process_rfc_physical(an_input)
    return a_response

@app.post("/get-rfc", tags=["Legacy"])
async def rfc_post(a_request: RequestRFC):    
    an_input = loads(a_request.json())
    
    a_response = engine.process_rfc_physical(an_input)
    return a_response

@app.get("/approve-alias/{alias}", tags=["Alias"], 
    response_model=OffensiveResponse)
async def alias_approval(alias: str): 
    a_response = engine.approve_alias(alias)
    return a_response


if __name__ == "__main__": 
    if debug: 
        uvicorn.run("__main__:app", port=80, host="0.0.0.0", reload=True)
    else:
        uvicorn.run(app, port=80, host="0.0.0.0")
