from datetime import datetime
from pydantic import BaseModel, Field

class UserSchema(BaseModel):
    id: str = Field(..., alias='_id')
    preferred_username: str
    picture: str
    given_name: str
    family_name: str
    email: str
    last_login: datetime