# Conversión de Flask a FastAPI y uvicorn.
# TODO: Better error handling with dates and errors raised.

import uvicorn
from fastapi import FastAPI
from json import loads

from app_fastapi import models
from src import engine

import config

SITE = config.SITE

app = FastAPI(title="Cálculo de RFC Personas Físicas",
    description="Aquí encontraras una manera de calcular el RFC completo con tu nombre y fecha de nacimiento (Personas Físicas). Asegurate de mandar en el campo de dateOfBirth la fecha de nacimiento en formato YYYY-DD-MM. Diego Villamil V1.0.0, FastAPI adaptation Marvin Nahmias V1.0.1.",
    version="1.0.1")


@app.get("/")
async def root():
    return {"Bienvenido!": "Consulta /docs para mas información del API de RFC calculador de homoclaves."}

# Este es el bueno. 
@app.get("/rfc_pf")
async def get_rfc(a_request: models.RequestRFC):    
    an_input = loads(a_request.json())
    
    a_response = engine.process_request(an_input, server="fastapi")
    return a_response


# Estos dos se habían compartido y se quedan para compatibilidad. 
@app.get("/get_rfc")
async def get_rfc(a_request: models.RequestRFC):    
    an_input = loads(a_request.json())
    a_response = engine.process_request(an_input, server="fastapi")
    return a_response

@app.post("/get_rfc")
async def get_rfc(a_request: models.RequestRFC):    
    an_input = loads(a_request.json())
    
    a_response = engine.process_request(an_input, server="fastapi")
    return a_response


 
if __name__ == "__main__": 
    uvicorn.run("__main__:app", port=80, host="0.0.0.0", reload=True)