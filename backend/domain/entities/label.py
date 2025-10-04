from pydantic import BaseModel, Field

class Label(BaseModel):
    id: str
    own_password: str
    com_password: str