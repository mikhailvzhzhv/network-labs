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
        self.MC_GROUP: str = MC_GROUP
        self.PORT: int = 1234
        self.ADDRESS: tuple = (self.MC_GROUP, self.PORT)
        self.copies: dict = dict()
        self.diconnected_copies: list = list()
        self.ttl: int = 32
        self.send_timer: Timer = Timer(500)
        self.family = socket.AF_INET6 if ":" in self.MC_GROUP else socket.AF_INET
        self.sock_sender: sock = sock(
            self.family, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        self.sock_receiver: sock = sock(
            self.family, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )

        match self.family:
            case socket.AF_INET:
                self.sock_sender.setsockopt(
                    socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ttl
                )
                self.sock_receiver.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                )
                self.sock_receiver.bind(("0.0.0.0", self.PORT))

                mreq = struct.pack(
                    "4sl", socket.inet_aton(self.MC_GROUP), socket.INADDR_ANY
                )
                self.sock_receiver.setsockopt(
                    socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq
                )
            case socket.AF_INET6:
                self.sock_sender.setsockopt(
                    socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, self.ttl
                )
                self.sock_receiver.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
                )
                self.sock_receiver.bind(("::", self.PORT))

                mreq = struct.pack(
                    "16s15s",
                    socket.inet_pton(socket.AF_INET6, self.MC_GROUP),
                    b"\0" * 15 + b"\001",
                )
                self.sock_receiver.setsockopt(
                    socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq
                )

        self.sock_receiver.settimeout(0.5)

    @stars_boarded
    def print_addrs(self) -> None:
        for address in self.copies.keys():
            print(address)

    def find_copy(self) -> None:
        print("Copy start...\n")

        while True:
            try:
                while True:
                    _, addr_from = self.sock_receiver.recvfrom(0)
                    if not self.copies.get(addr_from):
                        self.copies[addr_from] = Timer(4000)
                        print(f"Copy from {addr_from} connected")
                        self.print_addrs()
                    life_timer: Timer = self.copies.get(addr_from)
                    life_timer.reset()
            except TimeoutError:
                pass

            if self.send_timer.expired():
                self.sock_sender.sendto(bytes([]), self.ADDRESS)
                self.send_timer.reset()

            for address, life_timer in self.copies.items():
                if life_timer.expired():
                    self.diconnected_copies.append(address)

            if len(self.diconnected_copies) != 0:
                for address in self.diconnected_copies:
                    print(f"Copy from {address} disconnected")
                    self.copies.pop(address)

                self.print_addrs()
                self.diconnected_copies.clear()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Wanted <multicast group address>")
        exit()
    multicast_group: str = str(sys.argv[1])
    copy_finder: CopyFinder = CopyFinder(multicast_group)
    copy_finder.find_copy()
