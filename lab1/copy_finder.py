from timer import Timer

import socket
from socket import socket as sock
import struct
import sys


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
        self.__send_timer: Timer = Timer(500)
        self.__family = socket.AF_INET6 if ":" in self.__MC_GROUP else socket.AF_INET
        self.__sock_sender: sock = sock(
            self.__family, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        self.__sock_receiver: sock = sock(
            self.__family, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )

        match self.__family:
            case socket.AF_INET:
                self.__sock_sender.setsockopt(
                    socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.__ttl
                )
                self.__sock_receiver.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                )
                self.__sock_receiver.bind(("0.0.0.0", self.__PORT))

                mreq = struct.pack(
                    "4sl", socket.inet_aton(self.__MC_GROUP), socket.INADDR_ANY
                )
                self.__sock_receiver.setsockopt(
                    socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq
                )
            case socket.AF_INET6:
                self.__sock_sender.setsockopt(
                    socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, self.__ttl
                )
                self.__sock_receiver.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                )
                self.__sock_receiver.bind(("::", self.__PORT))

                mreq = struct.pack(
                    "16s15s",
                    socket.inet_pton(socket.AF_INET6, self.__MC_GROUP),
                    b"\0" * 15 + b"\001",
                )
                self.__sock_receiver.setsockopt(
                    socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq
                )

        self.__sock_receiver.settimeout(0.5)

    @stars_boarded
    def __print_addrs(self) -> None:
        for address in self.__copies.keys():
            print(address)

    def find_copy(self) -> None:
        print("Copy start...\n")

        while True:
            try:
                while True:
                    _, addr_from = self.__sock_receiver.recvfrom(0)
                    if not self.__copies.get(addr_from):
                        self.__copies[addr_from] = Timer(4000)
                        print(f"Copy from {addr_from} connected")
                        self.__print_addrs()
                    life_timer: Timer = self.__copies.get(addr_from)
                    life_timer.reset()
            except TimeoutError:
                pass

            if self.__send_timer.expired():
                self.__sock_sender.sendto(bytes([]), self.__ADDRESS)
                self.__send_timer.reset()

            for address, life_timer in self.__copies.items():
                if life_timer.expired():
                    self.__diconnected_copies.append(address)

            if len(self.__diconnected_copies) != 0:
                for address in self.__diconnected_copies:
                    print(f"Copy from {address} disconnected")
                    self.__copies.pop(address)

                self.__print_addrs()
                self.__diconnected_copies.clear()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Enter multicast group address")
        exit()
    multicast_group: str = str(sys.argv[1])
    copy_finder: CopyFinder = CopyFinder(multicast_group)
    copy_finder.find_copy()
