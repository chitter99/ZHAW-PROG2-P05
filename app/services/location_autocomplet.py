import requests

from .base import BaseService


class LocationAutocompletService(BaseService):
    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__()

    def search_completion(self, term, nofavorites=1, show_ids=0, show_coordinates=0):
        params = {
            "term": term,
            "nofavorites": nofavorites,
            "show_ids": show_ids,
            "show_coordinates": show_coordinates,
        }
        response = requests.get(self.url + "/completion.json", params=params)
        return response.json()
