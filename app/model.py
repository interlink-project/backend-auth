from datetime import datetime
from pydantic import BaseModel, Extra
from typing import Optional

class UserSchema(BaseModel, extra=Extra.ignore):
    _id: str
    sub: str
    zoneinfo: Optional[str]
    preferred_username: Optional[str]
    picture: Optional[str]
    given_name: Optional[str]
    family_name: Optional[str]
    email: Optional[str]
    last_login: datetime