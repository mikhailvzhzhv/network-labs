from time import time


class MillisGetter:
    def get_cur_ms(self) -> int:
        return int(round(time() * 1000))


class Timer(MillisGetter):
    def __init__(self, millis: int) -> None:
        self.ms: int = millis
        self.start_time: int = self.get_cur_ms()

    def get_timeout(self) -> int:
        return self.ms

    def expired(self) -> bool:
        return self.get_cur_ms() > self.start_time + self.ms

    def reset(self) -> None:
        self.start_time = self.get_cur_ms()
