from pydantic import BaseModel

class AccessESPRequest(BaseModel):
    my_id: str
    seen_id: str
