from pydantic import BaseModel
from typing import Optional

class Position(BaseModel):
    label_id: str
    x: float
    y: float
    is_base_station: bool = False
    distance_to_base: Optional[float] = None  # Distance to first base station in meters
