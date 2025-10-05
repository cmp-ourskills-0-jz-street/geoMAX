from pydantic import BaseModel
from domain.entities.label import Label

class AccessRequest(BaseModel):
    own_id: str
    neighbour_id: str
    com_password: str
    own_password: str

    def to_own_label(self) -> Label:
        return Label(
            id=self.own_id,
            own_password=self.own_password,
            com_password=self.com_password,
        )