import requests

from ..models import Location, Connection, Coordinates, Prognosis, Stop, Journey, Section, Service
from .base import BaseService
from .. import utils

class TransportService(BaseService):
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__()

    def search_locations(self, query=None, x=None, y=None, location_type='all'):
        params = {'query': query, 'x': x, 'y': y, 'type': location_type}
        response = requests.get(self.url + "/locations", params=params)
        # We need to remove Nones for dict.get default to work
        data = utils.clean_nones(response.json())
        return [self.parse_location(item) for item in data.get('stations', [])]
    
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
        # We need to remove Nones for dict.get default to work
        data = utils.clean_nones(response.json())
        return [self.parse_connection(item) for item in data.get('connections', [])]

    def parse_location(self, data: dict) -> Location:
        coordinate_data = data.get('coordinate', {})
        coordinates = Coordinates(
            type=coordinate_data.get('type'),
            x=coordinate_data.get('x'),
            y=coordinate_data.get('y')
        )
        return Location(
            id=data.get('id'),
            type=data.get('type'),
            name=data.get('name'),
            score=data.get('score'),
            coordinate=coordinates,
            distance=data.get('distance')
        )

    def parse_prognosis(self, data: dict) -> Prognosis:
        return Prognosis(
            platform=data.get('platform'),
            departure=data.get('departure'),
            arrival=data.get('arrival'),
            capacity1st=data.get('capacity1st'),
            capacity2nd=data.get('capacity2nd')
        )

    def parse_stop(self, data: dict) -> Stop:
        prognosis_data = data.get('prognosis', {})
        prognosis = self.parse_prognosis(prognosis_data)
        station_data = data.get('station', {})
        station = self.parse_location(station_data)
        return Stop(
            station=station,
            arrival=data.get('arrival'),
            departure=data.get('departure'),
            delay=data.get('delay'),
            platform=data.get('platform'),
            prognosis=prognosis
        )

    def parse_journey(self, data: dict) -> Journey:
        pass_list_data = data.get('passList', [])
        pass_list = [self.parse_stop(stop_data) for stop_data in pass_list_data]
        return Journey(
            name=data.get('name'),
            category=data.get('category'),
            categoryCode=data.get('categoryCode'),
            number=data.get('number'),
            operator=data.get('operator'),
            to=data.get('to'),
            passList=pass_list,
            capacity1st=data.get('capacity1st'),
            capacity2nd=data.get('capacity2nd')
        )

    def parse_section(self, data: dict) -> Section:
        journey_data = data.get('journey', {})
        journey = self.parse_journey(journey_data)
        departure_data = data.get('departure', {})
        departure = self.parse_stop(departure_data)
        arrival_data = data.get('arrival', {})
        arrival = self.parse_stop(arrival_data)
        return Section(
            journey=journey,
            walk=data.get('walk'),
            departure=departure,
            arrival=arrival
        )

    def parse_service(self, data: dict) -> Service:
        return Service(
            regular=data.get('regular'),
            irregular=data.get('irregular')
        )


    def parse_connection(self, data: dict) -> Connection:
        section_data = data.get('sections', [])
        sections = [self.parse_section(section_item) for section_item in section_data]
        service_data = data.get('service', {})
        service = self.parse_service(service_data)
        return Connection(
            _from=self.parse_stop(data.get('from', {})),
            to=self.parse_stop(data.get('to', {})),
            duration=data.get('duration'),
            service=service,
            products=data.get('products'),
            capacity1st=data.get('capacity1st'),
            capacity2nd=data.get('capacity2nd'),
            transfers=data.get('transfers'),
            sections=sections
        )

    
