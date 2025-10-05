from data.repositories.label_repository import LabelRepository
from data.repositories.position_repository import PositionRepository
from domain.entities.label import Label
from domain.entities.access_request import AccessRequest
from domain.entities.signal_data import SignalData
from domain.entities.update_request import UpdateRequest
from domain.entities.position import Position
from core.errors import NotFoundLabelException, DismatchPasswordException
from core.geometry import calculate_position_from_signals
from typing import List, Dict

class LabelInteractor():
    def __init__(self, repository: LabelRepository, position_repository: PositionRepository = None):
        self.repository = repository
        self.position_repository = position_repository or PositionRepository()
        self._label_counter = 0

    def create(self, label: Label):
        self.repository.add(label)
        
        # Automatically assign base station positions for first 3 labels
        self._label_counter += 1
        if self._label_counter <= 3:
            # Set default positions for base stations
            # These will be overridden by user configuration
            if self._label_counter == 1:
                position = Position(label_id=label.id, x=0.0, y=0.0, is_base_station=True)
            elif self._label_counter == 2:
                position = Position(label_id=label.id, x=10.0, y=0.0, is_base_station=True)
            elif self._label_counter == 3:
                position = Position(label_id=label.id, x=0.0, y=10.0, is_base_station=True)
            
            self.position_repository.save_position(position)

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
    
    def post_update(self, update_request: UpdateRequest):
        """Process update with neighbor RSSI data and calculate position"""
        # Verify label exists
        label = self.repository.get_by_id(update_request.id)
        if not label:
            raise NotFoundLabelException("Label not found")
        
        # Get base stations configuration
        base_stations = {}
        all_positions = self.position_repository.get_all_positions()
        for label_id, position in all_positions.items():
            if position.is_base_station:
                base_stations[label_id] = {"x": position.x, "y": position.y}
        
        # Calculate position if we have enough base stations
        if len(base_stations) >= 3:
            result = calculate_position_from_signals(update_request.neighbors, base_stations)
            if result:
                x, y = result
                position = Position(label_id=update_request.id, x=x, y=y, is_base_station=False)
                self.position_repository.save_position(position)
    
    def post_signals(self, signal_data: SignalData):
        """Legacy method for signal data"""
        pass

    def delete(self, label_id: str):
        self.repository.delete(label_id)
    
    def get_all_positions(self) -> List[Dict]:
        """Get all positions for visualization"""
        positions = self.position_repository.get_all_positions()
        return [
            {
                "label_id": pos.label_id,
                "x": pos.x,
                "y": pos.y,
                "is_base_station": pos.is_base_station
            }
            for pos in positions.values()
        ]
    
    def configure_base_stations(self, config: Dict):
        """Configure base station positions from user input"""
        # Expected config format:
        # {
        #   "base_station_1": {"label_id": "...", "x": 0, "y": 0},
        #   "base_station_2": {"label_id": "...", "x": 10, "y": 0},
        #   "base_station_3": {"label_id": "...", "x": 0, "y": 10}
        # }
        for key, station_config in config.items():
            label_id = station_config.get("label_id")
            x = station_config.get("x", 0.0)
            y = station_config.get("y", 0.0)
            
            if label_id:
                position = Position(label_id=label_id, x=float(x), y=float(y), is_base_station=True)
                self.position_repository.save_position(position)
        
        self.position_repository.set_base_stations_config(config)
