import aiohttp
import asyncio
import sys

from global_var import WIDTH
from data_provider import DataProvider, Request


class PlaceInformer:
    def __init__(self, location: str) -> None:
        self.dataProvider = DataProvider(location)

    async def fetch_new_session(self, req: Request) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(req.getURL(), params=req.getQuery()) as response:
                return await response.json()

    async def fetch_passed_session(
        self, session: aiohttp.ClientSession, req: Request
    ) -> dict:
        async with session.get(req.getURL(), params=req.getQuery()) as response:
            return await response.json()

    async def fetch_all(self, reqs: list) -> list:
        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(*[self.fetch_passed_session(session, req) for req in reqs])

    async def run(self):
        geoResp = await self.fetch_new_session(self.dataProvider.geoRequest)
        self.dataProvider.setGeoResponse(geoResp)

        print("".center(WIDTH, "="))
        print("Locations".center(WIDTH))
        for g in self.dataProvider.geoRes.getLocations():
            print(g.getLocation())

        id: str = str(input("Wanted location id: "))
        trustId: bool = self.dataProvider.setLocationId(id)
        if not trustId:
            print("Id mismatch!")
            sys.exit()

        weatherResp, tripmapResp = await asyncio.gather(
            self.fetch_new_session(self.dataProvider.weatherRequest),
            self.fetch_new_session(self.dataProvider.tripmapRequest),
        )

        self.dataProvider.setWeatherResponse(weatherResp)
        self.dataProvider.setTripmapResponse(tripmapResp)

        descrResps = await self.fetch_all(self.dataProvider.descrRequest)
        self.dataProvider.setDescrResponses(descrResps)

        print("-" * WIDTH)
        print(self.dataProvider.weatherRes.getWeather())
        for i in range(len(self.dataProvider.descrRes)):
            print(
                "-" * WIDTH,
                self.dataProvider.tripmapRes.getPlaces()[i],
                self.dataProvider.descrRes[i].getDescription(),
                sep="\n",
                end="\n",
            )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Wanted: <location>")
        sys.exit()

    location: str = str(sys.argv[1])
    locationInformer: PlaceInformer = PlaceInformer(location)
    asyncio.run(locationInformer.run())
