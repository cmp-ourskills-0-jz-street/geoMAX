import math
from typing import Tuple, Optional, List

def rssi_to_distance(rssi: int, tx_power: int = -59, n: float = 2.0) -> float:
    """
    Convert RSSI to distance in meters using log-distance path loss model.
    
    Args:
        rssi: Received Signal Strength Indicator in dBm
        tx_power: Transmit power at 1 meter (calibration constant)
        n: Path loss exponent (2.0 for free space, 2-4 for indoor)
    
    Returns:
        Distance in meters
    """
    if rssi == 0:
        return -1.0
    
    ratio = (tx_power - rssi) / (10 * n)
    return math.pow(10, ratio)


def trilaterate(p1: Tuple[float, float], d1: float,
                p2: Tuple[float, float], d2: float,
                p3: Tuple[float, float], d3: float) -> Optional[Tuple[float, float]]:
    """
    Calculate position using trilateration from 3 points.
    
    Args:
        p1, p2, p3: (x, y) coordinates of the three reference points
        d1, d2, d3: distances from the unknown point to each reference point
    
    Returns:
        (x, y) coordinates of the calculated position, or None if calculation fails
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    
    # Using the equations for trilateration
    A = 2 * (x2 - x1)
    B = 2 * (y2 - y1)
    C = d1**2 - d2**2 - x1**2 + x2**2 - y1**2 + y2**2
    
    D = 2 * (x3 - x2)
    E = 2 * (y3 - y2)
    F = d2**2 - d3**2 - x2**2 + x3**2 - y2**2 + y3**2
    
    # Solve the system of equations
    denominator = (A * E - B * D)
    if abs(denominator) < 1e-10:
        return None
    
    x = (C * E - F * B) / denominator
    y = (C * D - A * F) / denominator
    
    return (x, y)


def calculate_position_from_signals(signals: dict, base_stations: dict) -> Optional[Tuple[float, float]]:
    """
    Calculate position from signal strengths to multiple base stations.
    
    Args:
        signals: dict of {base_station_id: rssi}
        base_stations: dict of {base_station_id: {"x": float, "y": float}}
    
    Returns:
        (x, y) coordinates or None if not enough data
    """
    # Get the three strongest signals that are also base stations
    available_bases = []
    for bs_id, rssi in signals.items():
        if bs_id in base_stations:
            distance = rssi_to_distance(rssi)
            available_bases.append((bs_id, rssi, distance))
    
    if len(available_bases) < 3:
        return None
    
    # Sort by RSSI (strongest first) and take top 3
    available_bases.sort(key=lambda x: x[1], reverse=True)
    top_3 = available_bases[:3]
    
    # Get positions and distances
    positions = []
    distances = []
    for bs_id, rssi, distance in top_3:
        bs = base_stations[bs_id]
        positions.append((bs["x"], bs["y"]))
        distances.append(distance)
    
    # Trilaterate
    result = trilaterate(positions[0], distances[0],
                        positions[1], distances[1],
                        positions[2], distances[2])
    
    return result
