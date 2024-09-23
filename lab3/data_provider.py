import os
from typing import List
from dotenv import load_dotenv

from schemas.query import Query
from schemas.coordinates import Coord
from schemas.geo.geo_query import GeoQuery
from schemas.geo.geo_response import GeoResponse
from schemas.weather.weather_query import WeatherQuery
from schemas.weather.weather_response import WeatherResponse
from schemas.tripmap_place.tripmap_query import TripMapQuery
from schemas.tripmap_place.tripmap_resporse import TripmapResponse
from schemas.tripmap_descr.tripmap_descr_query import DescrQuery
from schemas.tripmap_descr.tripmap_descr_resp import DescrResponse

load_dotenv()

GEO_URL = os.getenv("GEO_URL")
WEATHER_URL = os.getenv("WEATHER_URL")
TRIPMAP_URL = os.getenv("TRIPMAP_URL")
DESCR_URL = os.getenv("DESCR_URL")


class Request:
    def __init__(self, url: str, q: Query) -> None:
        self.url = url
        self.q = q

    def getURL(self) -> str:
        return self.url

    def getQuery(self) -> dict:
        return self.q.toJson()


class DataProvider:
    def __init__(self, location: str) -> None:
        self.geoRequest: Request = Request(GEO_URL, GeoQuery(location))
        self.geoRes: GeoResponse = None
        self.weatherRes: WeatherResponse = None
        self.weatherRequest: Request = None
        self.tripmapRes: TripmapResponse = None
        self.tripmapRequest: Request = None
        self.descrRequest: List[Request] = []
        self.descrRes: List[DescrResponse] = []

    def setGeoResponse(self, geoResp: dict) -> None:
        self.geoRes = GeoResponse(**geoResp)

    def setLocationId(self, id: str) -> bool:
        c: Coord = self.geoRes.getCoordById(id)
        if c is None:
            return False

        self.weatherRequest = Request(WEATHER_URL, WeatherQuery(c))
        self.tripmapRequest = Request(TRIPMAP_URL, TripMapQuery(coord=c))
        return True

    def setWeatherResponse(self, weatherResp: dict) -> None:
        WeatherResponse.formatResponse(weatherResp)
        self.weatherRes = WeatherResponse(**weatherResp)

    def setTripmapResponse(self, tripmapRes: dict) -> None:
        self.tripmapRes = TripmapResponse(**tripmapRes)

        self.descrRequest.clear()
        for feature in self.tripmapRes.features:
            url = DESCR_URL + f"/{feature.properties.xid}"
            self.descrRequest.append(Request(url, DescrQuery()))

    def setDescrResponses(self, descrResps: List[dict]) -> None:
        for r in descrResps:
            r = DescrResponse.formatResponse(r)
            self.descrRes.append(DescrResponse(**r))
