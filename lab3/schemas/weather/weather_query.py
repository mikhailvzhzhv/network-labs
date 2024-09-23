from dotenv import load_dotenv
import os

from schemas.query import Query
from schemas.coordinates import Coord

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")


class WeatherQuery(Query):
    def __init__(self, coord: Coord) -> None:
        self.lat = coord.getLat()
        self.lon = coord.getLng()
        self.appid = API_KEY
