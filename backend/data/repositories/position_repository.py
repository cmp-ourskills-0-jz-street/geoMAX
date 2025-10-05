from typing import Dict, Optional
from domain.entities.position import Position

class PositionRepository:
    """In-memory storage for positions"""
    def __init__(self):
        self._positions: Dict[str, Position] = {}
        self._base_stations_config: Dict = {}
    
    def save_position(self, position: Position):
        """Save or update a position"""
        self._positions[position.label_id] = position
    
    def get_position(self, label_id: str) -> Optional[Position]:
        """Get position by label ID"""
        return self._positions.get(label_id)
    
    def get_all_positions(self) -> Dict[str, Position]:
        """Get all positions"""
        return self._positions.copy()
    
    def set_base_stations_config(self, config: Dict):
        """Set base stations configuration"""
        self._base_stations_config = config
    
    def get_base_stations_config(self) -> Dict:
        """Get base stations configuration"""
        return self._base_stations_config.copy()
