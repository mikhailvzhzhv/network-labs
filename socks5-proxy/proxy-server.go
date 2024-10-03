package main

import (
	"fmt"
	"net"
	"os"
)

func main() {
	port := 1234
	listener, err := net.ListenTCP("tcp4", &net.TCPAddr{Port: port})
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return
	}

	for {
		conn, err := listener.AcceptTCP()
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return
		}
		go handleConnection(conn)
	}
}

func handleConnection(conn *net.TCPConn) {
	defer conn.Close()

	handshake(conn)
}

func handshake(conn *net.TCPConn) error {
	ver := make([]byte, 1)
	conn.Read(ver)
	if ver[0] != VER {
		return RaiseHandshakeError("SOCKS version not 5")
	}

	nauth := make([]byte, 1)
	conn.Read(nauth)

	auth := make([]byte, int(nauth[0]))
	n, _ := conn.Read(auth)

	var authmethod byte = CAUTHF
	for i := 0; i < n; i++ {
		if auth[i] == AUTH {
			authmethod = CAUTH
			break
		}
	}

	ans := []byte{VER, authmethod}
	conn.Write(ans)

	return nil
}
