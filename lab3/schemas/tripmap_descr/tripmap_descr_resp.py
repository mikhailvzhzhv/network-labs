from global_var import WIDTH


class WikipediaExtracts:
    def __init__(self, title: str, text: str, html: str):
        self.title = title
        self.text = text
        self.html = html


class Info:
    def __init__(self, src: str, src_id: int, descr: str, **others):
        self.src = src
        self.src_id = src_id
        self.descr = descr


class Address:
    def __init__(
        self,
        city: str,
        state: str,
        suburb: str,
        country: str,
        postcode: str,
        country_code: str,
        city_district: str,
        road: str = None,
        house: str = None,
        house_number: str = None,
        footway: str = None,
        county: str = None,
    ):
        self.city = city
        self.state = state
        self.suburb = suburb
        self.country = country
        self.footway = footway
        self.postcode = postcode
        self.country_code = country_code
        self.city_district = city_district
        self.road = road
        self.house = house
        self.house_number = house_number
        self.county = country


class DescrResponse:
    def __init__(
        self,
        xid: str,
        name: str,
        wikipedia_extracts: dict = None,
        url: str = None,
        info: dict = None,
    ):
        self.xid = xid
        self.name = name
        self.wikipedia_extracts = (
            WikipediaExtracts(**wikipedia_extracts)
            if wikipedia_extracts is not None
            else None
        )
        self.url = url
        self.info = Info(**info) if info is not None else None

    @staticmethod
    def formatResponse(descrResp: dict) -> None:
        r = dict()
        r["xid"] = descrResp["xid"]
        r["name"] = descrResp["name"]
        if descrResp.get("url"):
            r["url"] = descrResp["url"]
        if descrResp.get("wikipedia_extracts"):
            r["wikipedia_extracts"] = descrResp["wikipedia_extracts"]
        if descrResp.get("info"):
            r["info"] = descrResp["info"]
        return r

    def getDescription(self) -> str:
        descr: str = str()
        descr += "Description".center(WIDTH) + "\n"
        if self.url is not None:
            descr += f"url: {self.url}\n"
        if self.wikipedia_extracts is not None:
            descr += self.split_string(f"wiki: {self.wikipedia_extracts.text}\n")
        if self.info is not None:
            descr += f"descr: {self.info.descr}\n"

        return descr

    def split_string(self, string: str, length: int = WIDTH):
        return "\n".join(
            [string[i : i + length] for i in range(0, len(string), length)]
        )
