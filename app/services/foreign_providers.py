#!/usr/bin/env python3
""" TransportApp """

__author__ = "Aghrabi Carim, Zambelli Adrian, Schmid Aaron"
__version__ = "1.0.0"

import csv

from .base import BaseService
from .. import models


class ForeignProvidersService(BaseService):
    def __init__(self, path: str) -> None:
        self.path = path
        self.load_from_file()
        super().__init__()

    def load_from_file(self):
        self.providers = []
        with open(self.path, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                provider = models.ForeignProvider(
                    country=row["country"],
                    country_code=row["code"],
                    name=row["name"],
                    url=row["url"],
                )
                self.providers.append(provider)
        return self.providers

    def get(self, country_code) -> models.ForeignProvider:
        for provider in self.providers:
            if provider.country_code == country_code:
                return provider
        return None
