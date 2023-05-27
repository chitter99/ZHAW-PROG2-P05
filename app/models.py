from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class Route:
    start: str
    dest: str
    found_connection: bool
    coverage: float = 0
    direct_route: Optional[bool] = None
    # TODO: Define type for connections
    connections: Optional[Any] = None
    nearest_startion: Optional[str] = None