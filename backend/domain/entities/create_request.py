from pydantic import BaseModel

class CreateRequest(BaseModel):
    id: str
