from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import List, Any, Optional
from orjson import dumps


class PersonPhysical(BaseModel): 
    dateOfBirth: str
    firstName:   str
    lastName:    Optional[str] = None
    maternalLastName: Optional[str] = None
    

class RequestRFC(BaseModel): 
    personPhysical: PersonPhysical



class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return dumps(content)


