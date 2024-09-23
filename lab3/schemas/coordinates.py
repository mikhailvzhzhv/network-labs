class Coord:
    def __init__(self, lng: float, lat: float):
        self.lng = lng
        self.lat = lat

    def getLng(self) -> float:
        return self.lng

    def getLat(self) -> float:
        return self.lat
