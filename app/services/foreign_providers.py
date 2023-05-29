import csv

from .base import BaseService
from .. import models


class ForeignProvidersService(BaseService):
    def __init__(self, path: str) -> None:
        self.path = path
        self.load_from_file()
        super().__init__()

    def load_from_file(self):
        providers = []
        with open(self.path, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                provider = models.ForeignProvider(
                    country=row["country"],
                    country_code=row["code"],
                    name=row["name"],
                    url=row["url"],
                )
                providers.append(provider)
        return providers

    def get(self, country_code):
        for provider in self.providers:
            if provider.country_code == country_code:
                return provider
        return None
