from typing import List
from schemas.coordinates import Coord
from global_var import WIDTH


class Geometry:
    def __init__(self, type: str, coordinates: list):
        self.type = type
        self.coordinates = Coord(coordinates[1], coordinates[0])


class Properties:
    def __init__(
        self,
        xid: str,
        name: str,
        dist: float,
        rate: int,
        kinds: str,
        wikidata: str = None,
        osm: str = None,
    ):
        self.xid = xid
        self.name = name
        self.dist = dist
        self.rate = rate
        self.kinds = kinds
        self.osm = osm
        self.wikidata = wikidata


class Feature:
    def __init__(self, type: str, id: str, geometry: dict, properties: dict):
        self.type = type
        self.id = id
        self.geometry = Geometry(**geometry)
        self.properties = Properties(**properties)


class TripmapResponse:
    def __init__(self, type: str, features: dict):
        self.type = type
        self.features = [Feature(**feature) for feature in features]

    def getPlaces(self) -> List[str]:
        places: list = list()
        for feature in self.features:
            description: str = str()
            description += f"{feature.properties.name}".center(WIDTH) + "\n"
            description += f"dictance: {round(feature.properties.dist, 0)}m\n"
            description += f"rate: {feature.properties.rate}/10\n"
            places.append(description)

        return places
