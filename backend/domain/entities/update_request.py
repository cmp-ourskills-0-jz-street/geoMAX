from pydantic import BaseModel
from typing import Dict

class UpdateRequest(BaseModel):
    id: str
    neighbors: Dict[str, int]  # neighbor_id -> rssi
