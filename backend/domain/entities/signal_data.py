from pydantic import BaseModel, Field

class Signal(BaseModel):
    id: str
    rssi: int

class SignalData(BaseModel):
    own_id: str = Field(alias='id')
    data: list[Signal]