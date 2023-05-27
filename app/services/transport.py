import requests

from .base import BaseService

class TransportService(BaseService):
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__()

    def search_locations(self, query=None, x=None, y=None, location_type='all'):
        params = {'query': query, 'x': x, 'y': y, 'type': location_type}
        response = requests.get(self.url + "/locations", params=params)
        return response.json()
    
    def get_connections(self, departure, arrival, via=None, date=None, time=None, is_arrival_time=None,
                    transportations=None, limit=None, page=None, direct=None, sleeper=None,
                    couchette=None, bike=None, accessibility=None):
        params = {
            'from': departure,
            'to': arrival,
            'via': via,
            'date': date,
            'time': time,
            'isArrivalTime': is_arrival_time,
            'transportations': transportations,
            'limit': limit,
            'page': page,
            'direct': direct,
            'sleeper': sleeper,
            'couchette': couchette,
            'bike': bike,
            'accessibility': accessibility
        }
        response = requests.get(self.url + "/connections", params=params)
        return response.json()
    
