
from .base import BaseService
from .transport import TransportService

class TransportCacheService(BaseService):
    def __init__(self, transport_service: TransportService) -> None:
        self.transport_service = transport_service
        super().__init__()

    def get_connections(self):
        pass
            

