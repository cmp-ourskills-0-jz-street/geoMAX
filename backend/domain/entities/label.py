from pydantic import BaseModel, Field

class Label(BaseModel):
    id: str = Field(alias='id')
    own_password: str
    com_password: str