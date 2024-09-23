import os
from dotenv import load_dotenv

from schemas.query import Query

load_dotenv()

API_KEY = os.getenv("TRIPMAP_API_KEY")

class DescrQuery(Query):
    def __init__(self) -> None:
        self.apikey: str = API_KEY
