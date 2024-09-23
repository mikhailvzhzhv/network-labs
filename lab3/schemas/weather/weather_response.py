from schemas.coordinates import Coord


class Weather:
    def __init__(self, id: int, main: str, description: str, icon: str):
        self.id = id
        self.main = main
        self.description = description
        self.icon = icon


class Main:
    def __init__(
        self,
        temp: float,
        feels_like: float,
        temp_min: float,
        temp_max: float,
        pressure: int,
        humidity: int,
        sea_level: int,
        grnd_level: int,
    ):
        self.temp = temp
        self.feels_like = feels_like
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.pressure = pressure
        self.humidity = humidity
        self.sea_level = sea_level
        self.grnd_level = grnd_level


class Wind:
    def __init__(self, speed: float, deg: int, gust: float = None):
        self.speed = speed
        self.deg = deg
        self.gust = gust


class Rain:
    def __init__(self, _1h: float):
        self._1h = _1h


class Snow:
    def __init__(self, _1h: float):
        self._1h = _1h


class Clouds:
    def __init__(self, all: int):
        self.all = all


class Sys:
    def __init__(
        self, country: str, sunrise: int, sunset: int, type: int = None, id: int = None
    ):
        self.type = type
        self.id = id
        self.country = country
        self.sunrise = sunrise
        self.sunset = sunset


class WeatherResponse:
    def __init__(
        self,
        coord: dict,
        weather: list,
        base: str,
        main: dict,
        visibility: int,
        wind: dict,
        clouds: dict,
        dt: int,
        sys: dict,
        timezone: int,
        id: int,
        name: str,
        cod: int,
        rain: dict = None,
        snow: dict = None,
    ):
        self.coord = Coord(coord["lon"], coord["lat"])
        self.weather = weather
        self.base = base
        self.main = Main(**main)
        self.visibility = visibility
        self.wind = Wind(**wind)
        self.rain = Rain(**rain) if rain is not None else None
        self.snow = Snow(**snow) if snow is not None else None
        self.clouds = Clouds(**clouds)
        self.dt = dt
        self.sys = Sys(**sys)
        self.timezone = timezone
        self.id = id
        self.name = name
        self.cod = cod

    def getWeather(self) -> str:
        def toC(t: float) -> float:
            return round(t - 273.15, 0)

        weather: str = str()
        weather += "Weather".center(70) + "\n"
        weather += f"temperature: {toC(self.main.temp)}C\n"
        weather += f"feel like: {toC(self.main.feels_like)}C\n"
        weather += f"humidity: {self.main.humidity}%\n"
        weather += f"visibility: {self.visibility}m\n"
        weather += f"wind speed: {self.wind.speed}m/s\n"
        weather += f"clouds: {self.clouds.all}%\n"

        if self.rain is not None:
            weather += f"rain: {self.rain._1h}mm/s\n"
        if self.snow is not None:
            weather += f"snow: {self.snow._1h}mm/s\n"

        return weather

    @staticmethod
    def formatResponse(wresp: dict):
        if wresp.get("snow"):
            wresp["snow"]["_1h"] = wresp["snow"].pop("1h")
        if wresp.get("rain"):
            wresp["rain"]["_1h"] = wresp["rain"].pop("1h")
