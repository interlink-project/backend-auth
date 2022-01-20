from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class UserSchema(BaseModel):
    id: str = Field(..., alias='_id')
    preferred_username: Optional[str]
    picture: Optional[str]
    given_name: Optional[str]
    family_name: Optional[str]
    email: Optional[str]
    last_login: datetime