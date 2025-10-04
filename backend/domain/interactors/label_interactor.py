from data.repositories.label_repository import LabelRepository
from domain.entities.label import Label
from domain.entities.access_request import AccessRequest
from domain.entities.signal_data import SignalData
from core.errors import NotFoundLabelException, DismatchPasswordException

class LabelInteractor():
    def __init__(self, repository: LabelRepository):
        self.repository = repository

    def create(self, label: Label):
        self.repository.add(label)

    def access_request(self, access_request: AccessRequest):
        existing_label = self.repository.get_by_id(access_request.own_id)
        if not existing_label:
            raise NotFoundLabelException("not found label sender")
        
        neighbour_label = self.repository.get_by_id(access_request.neighbour_id)
        if not neighbour_label:
            raise NotFoundLabelException("not found label recipient")
        
        own_label = access_request.to_own_label()

        if existing_label.com_password != own_label.com_password:
            raise DismatchPasswordException("com passwords don't match")
        
        if existing_label.own_password != own_label.own_password:
            raise DismatchPasswordException("own passwords don't match")
    
    def post_signals(self, neighbours: list[SignalData]):
        pass

    def delete(self, label_id: str):
        self.repository.delete(label_id)
