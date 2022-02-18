from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import Any, Optional
from orjson import dumps
from src.get_rfc import PersonPhysical



class RequestRFC(BaseModel): 
    personPhysical: PersonPhysical


class OffensiveResponse(BaseModel): 
    alias : str
    offense: Optional[str] = None
    offenseType: Optional[str] = None


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return dumps(content)


