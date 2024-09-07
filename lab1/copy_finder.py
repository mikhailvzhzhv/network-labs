from timer import Timer

import socket
from socket import socket as sock
import struct


def stars_boarded(f):
    def out(*args):
        print("\n" + "*" * 20)
        f(*args)
        print("*" * 20 + "\n")

    return out


class CopyFinder:
    def __init__(self, MC_GROUP) -> None:
        self.__MC_GROUP: str = MC_GROUP
        self.__PORT: int = 1234
        self.__ADDRESS: tuple = (self.__MC_GROUP, self.__PORT)
        self.__copies: dict = dict()
        self.__diconnected_copies: list = list()
        self.__ttl: int = 32
        self.__timer: Timer = Timer(1000)
        self.__sock_sender: sock = sock(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        self.__sock_receiver: sock = sock(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )

        self.__sock_sender.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.__ttl
        )
        self.__sock_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock_receiver.bind(self.__ADDRESS)

        mreq = struct.pack("4sl", socket.inet_aton(self.__MC_GROUP), socket.INADDR_ANY)
        self.__sock_receiver.setsockopt(
            socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq
        )
        self.__sock_receiver.settimeout(1)

    @stars_boarded
    def __print_addrs(self) -> None:
        for address in self.__copies.keys():
            print(address)

    def find_copy(self) -> None:
        print("Copy start...\n")

        while True:
            try:
                while True:
                    _, addr_from = self.__sock_receiver.recvfrom(10)
                    if not self.__copies.get(addr_from):
                        self.__copies[addr_from] = Timer(3000)
                        print(f"Copy from {addr_from} connected")
                        self.__print_addrs()
                    life_timer: Timer = self.__copies.get(addr_from)
                    life_timer.reset()
            except TimeoutError:
                pass

            if self.__timer.expired():
                self.__sock_sender.sendto(bytes([]), self.__ADDRESS)
                self.__timer.reset()

            for address, life_timer in self.__copies.items():
                if life_timer.expired():
                    self.__diconnected_copies.append(address)

            for address in self.__diconnected_copies:
                print(f"Copy from {address} disconnected")
                self.__copies.pop(address)

            if len(self.__diconnected_copies) != 0:
                self.__print_addrs()
                self.__diconnected_copies.clear()


if __name__ == "__main__":
    multicast_group: str = str(input())
    copy_finder: CopyFinder = CopyFinder(multicast_group)
    copy_finder.find_copy()
