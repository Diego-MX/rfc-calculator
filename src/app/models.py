# pylint: disable=no-name-in-module
# pylint: disable=too-few-public-methods
from typing import Optional, ClassVar, Dict, Any

from fastapi.responses import JSONResponse
from orjson import dumps 
from pydantic import BaseModel      
from toolz import valmap

from src.get_rfc import PersonPhysical

class CustomModel(BaseModel): 
    @classmethod
    def from_gen(cls, gen): 
        return cls(**dict(zip(cls.__fields__, gen)))


class RequestValidation(BaseModel): 
    userRFC: str
    calculatedRFC: str


class RequestRFC(BaseModel): 
    personPhysical: PersonPhysical


class RFCValidationResponse(BaseModel): 
    key: int
    name: str
    message: str
    messages: ClassVar[Dict] = {
        '-1': ('RFC Válido', "Tu RFC es válido"), 
        '-2': ('RFC Inválido', "Tu RFC tiene errores, ingrésalo nuevamente"),
        '-3': ('Error no reconocido', "Tu RFC no se puede determinar"),
        '-4': ('RFC Incompleto', "Tu RFC no contiene homoclave, pero la base es correcta"), 
        '0' : ('Formato', "El formato de tu RFC es incorrecto, ingrésalo nuevamente"), 
        '1' : ('Dígito verificador', 
               "El último dígito de tu RFC no corresponde, ingrésalo correctamente"), 
        '2' : ('Homoclave', "La homoclave de tu RFC no coincide, ingrésala nuevamente"), 
        '3' : ('Fecha de nacimiento', 
               "La fecha de nacimiento de tu RFC no coincide, ingrésala nuevamente"), 
        '4' : ('Iniciales', "Las iniciales de tu RFC no corresponden, ingrésalas nuevamente")}
    
    @classmethod
    def from_key(cls, a_key): 
        b_key = str(a_key) 
        c_key = b_key if b_key in cls.messages else '-3'
        c_msg = cls.messages[c_key] 
        c_obj = cls(key=c_key, name=c_msg[0], message=c_msg[1])
        return c_obj


class OffensiveResponse(CustomModel): 
    alias : str
    offense: Optional[str] = None
    offenseType: Optional[str] = None

    def fprint(self):
        none_str = lambda ss: ss or ""
        str_dict = valmap(none_str, self.dict())
        return "{alias:16}{offense:10}{offenseType:12}".format(**str_dict) 


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content:Any) -> bytes:
        return dumps(content)
