from dotenv import load_dotenv
import os
from schemas.query import Query

load_dotenv()

API_KEY = os.getenv("GEO_API_KEY")

class GeoQuery(Query):
    def __init__(self, location: str) -> None:
        self.q: str = location
        self.locale = "en"
        self.limit = "5"
        self.reverse = "false"
        self.debug = "false"
        self.point = ""
        self.provider = "default"
        self.key = API_KEY
