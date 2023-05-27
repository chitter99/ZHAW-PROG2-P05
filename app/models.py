from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class Route:
    start: str
    dest: str
    direct_route: bool
    coverage: float
    # TODO: Define type for connections
    connections: Any
    nearest_startion: Optional[str] = None