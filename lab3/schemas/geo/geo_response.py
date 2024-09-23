from typing import List
from schemas.coordinates import Coord


class GeoLocation:
    def __init__(
        self,
        point: dict,
        osm_id: int,
        osm_type: str,
        country: str,
        osm_key: str,
        osm_value: str,
        name: str,
        countrycode: str = None,
        city: str = None,
        state: str = None,
        street: str = None,
        housenumber: str = None,
        house_number: str = None,
        postcode: str = None,
        extent: list = None,
    ):
        self.point = Coord(**point)
        self.osm_id = osm_id
        self.osm_type = osm_type
        self.country = country
        self.osm_key = osm_key
        self.osm_value = osm_value
        self.name = name
        self.countrycode = countrycode
        self.city = city
        self.state = state
        self.street = street
        self.housenumber = housenumber or house_number
        self.postcode = postcode
        self.extent = extent if extent else []

    def getLocation(self) -> str:
        location: str = str()
        location += f"id: {self.osm_id}\n"
        if self.country is not None:
            location += f"country: {self.country}\n"
        if self.name is not None:
            location += f"name: {self.name}\n"
        if self.city is not None:
            location += f"city: {self.city}\n"
        if self.street is not None:
            location += f"street: {self.street}\n"
        if self.housenumber is not None:
            location += f"housenumber: {self.housenumber}\n"

        return location


class GeoResponse:
    def __init__(self, hits: list, locale: str):
        self.hits = [GeoLocation(**hit) for hit in hits]
        self.locate = locale

    def getLocations(self) -> List[GeoLocation]:
        return self.hits
    
    def getCoordById(self, id: str) -> Coord:
        for g in self.hits:
            if str(g.osm_id) == id:
                return g.point

        return None
