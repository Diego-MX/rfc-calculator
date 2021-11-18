from pydantic import BaseModel
from typing import Optional


class PersonPhysical(BaseModel): 
    dateOfBirth: str
    firstName:   str
    lastName:  Optional[str] = None
    maternalLastName: Optional[str] = None
    

class RequestRFC(BaseModel): 
    personPhysical: PersonPhysical
