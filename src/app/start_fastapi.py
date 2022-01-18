# Conversión de Flask a FastAPI y uvicorn.
# TODO: Better error handling with dates and errors raised.
import sys
from fastapi import FastAPI
from json import loads
import uvicorn

from .models import (ORJSONResponse, RequestRFC)
from src import engine
from config import VERSION

debug = ("debug" in sys.argv)

app = FastAPI(title="Cálculo de RFC Personas Físicas",
    description=f"Aquí encontraras una manera de calcular el RFC completo con tu nombre y fecha de nacimiento (Personas Físicas). Asegurate de mandar en el campo de dateOfBirth la fecha de nacimiento en formato YYYY-DD-MM.",
    version=VERSION, 
    default_response_class=ORJSONResponse)

@app.get("/")
async def root():
    return f"Uploaded, version: {VERSION}"


# Este es el bueno. 
@app.get("/rfc-pf")
async def get_rfc(a_request: RequestRFC):    
    an_input = loads(a_request.json())    
    a_response = engine.process_request(an_input, server="fastapi")
    return a_response


# Estos dos se habían compartido y se quedan para compatibilidad. 
@app.get("/get-rfc")
async def get_rfc(a_request: RequestRFC):    
    an_input = loads(a_request.json())
    a_response = engine.process_request(an_input, server="fastapi")
    return a_response

@app.post("/get-rfc")
async def get_rfc(a_request: RequestRFC):    
    an_input = loads(a_request.json())
    
    a_response = engine.process_request(an_input, server="fastapi")
    return a_response


if __name__ == "__main__": 
    if debug: 
        uvicorn.run("__main__:app", port=80, host="0.0.0.0", reload=True)
    else:
        uvicorn.run(app, port=80, host="0.0.0.0")
