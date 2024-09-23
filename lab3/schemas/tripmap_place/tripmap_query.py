import os
from dotenv import load_dotenv

from schemas.query import Query
from schemas.coordinates import Coord

load_dotenv()
API_KEY = os.getenv("TRIPMAP_API_KEY")


class TripMapQuery(Query):
    def __init__(self, coord: Coord, radius: int = 1000, limit: int = 5):
        self.lang = "en"
        self.radius = radius
        self.lon = coord.getLng()
        self.lat = coord.getLat()
        self.limit = limit
        self.rate = "3h"
        self.apikey = API_KEY
