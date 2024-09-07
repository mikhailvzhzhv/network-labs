from time import time


class MillisGetter:
    def get_cur_ms(self) -> int:
        return int(round(time() * 1000))


class Timer(MillisGetter):
    def __init__(self, millis: int) -> None:
        self.__ms: int = millis
        self.__start_time: int = self.get_cur_ms()

    def get_timeout(self) -> int:
        return self.__ms

    def expired(self) -> bool:
        return self.get_cur_ms() > self.__start_time + self.__ms

    def reset(self) -> None:
        self.__start_time = self.get_cur_ms()
