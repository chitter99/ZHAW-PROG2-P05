#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

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
