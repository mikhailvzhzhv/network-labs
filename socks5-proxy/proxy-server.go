package main

import (
	"encoding/binary"
	"fmt"
	"io"
	"net"
	"os"
	"sync"
)

func main() {
	port := 1234
	listener, err := net.ListenTCP("tcp4", &net.TCPAddr{Port: port})
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return
	}

	for {
		client, err := listener.AcceptTCP()
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return
		}
		go handleConnection(client)
	}
}

func handleConnection(client *net.TCPConn) {
	defer client.Close()

	err := handshake(client)
	if err != nil {
		fmt.Fprintln(os.Stderr, err.Error())
		return
	}

	peer, status, err := getConnection(client)
	if err != nil {
		fmt.Fprintln(os.Stderr, err.Error())
		return
	}

	sendCommandReply(peer, status)

	transferData(client, peer)
}

func handshake(client *net.TCPConn) error {
	ver := make([]byte, 1)
	client.Read(ver)
	if ver[0] != VER {
		return RaiseHandshakeError("SOCKS version not 5")
	}

	nauth := make([]byte, 1)
	client.Read(nauth)

	authmethod, err := getAvaliableMethods(client, nauth[0])

	ans := []byte{VER, authmethod}
	client.Write(ans)

	if err != nil {
		return err
	}

	return nil
}

func getAvaliableMethods(client *net.TCPConn, n byte) (byte, error) {
	methods := make([]byte, n)
	client.Read(methods)
	for i := 0; i < int(n); i++ {
		if methods[i] == AUTH {
			return CAUTH, nil
		}
	}
	return CAUTHF, RaiseHandshakeError("no acceptable methods were offered")
}

func getConnection(client *net.TCPConn) (*net.TCPConn, byte, error) {
	ver := make([]byte, 1)
	client.Read(ver)
	if ver[0] != VER {
		return nil, GENERAL_FAILURE, RaiseConnectionError("SOCKS version not 5")
	}

	cmd := make([]byte, 1)
	client.Read(cmd)
	if cmd[0] != CMD {
		return nil, COMMAND_NOT_SUPPORTED, RaiseConnectionError("command not supported")
	}

	rsv := make([]byte, 1)
	client.Read(rsv)
	if rsv[0] != RSV {
		return nil, GENERAL_FAILURE, RaiseConnectionError("rsv not 0")
	}

	typeaddrs := make([]byte, 1)
	client.Read(typeaddrs)

	switch typeaddrs[0] {
	case TYPEipv4:
		ip, port := handleIPv4(client)
		return clientectIPv4(ip, port)
	case TYPEdn:
		dn, port := handleDomainName(client)
		return clientectDN(dn, port)
	default:
		return nil, ADDRESS_TYPE_NOT_SUPPORTED, RaiseConnectionError("address type not supported")
	}
}

func handleIPv4(client *net.TCPConn) ([]byte, int) {
	ip := make([]byte, 4)
	client.Read(ip)

	portb := make([]byte, 2)
	client.Read(portb)
	port := int(binary.BigEndian.Uint16(portb))

	return ip, port
}

func clientectIPv4(ipv4 net.IP, port int) (*net.TCPConn, byte, error) {
	ip := net.TCPAddr{IP: ipv4, Port: port}
	peer, err := net.DialTCP("tcp4", nil, &ip)

	fmt.Println("Destination address: ", peer.RemoteAddr())

	return peer, REQUEST_GRANTED, err
}

func handleDomainName(client *net.TCPConn) (string, int) {
	l := make([]byte, 1)
	client.Read(l)

	dn := make([]byte, l[0])
	client.Read(dn)

	portb := make([]byte, 2)
	client.Read(portb)
	port := int(binary.BigEndian.Uint16(portb))

	return string(dn), port
}

func clientectDN(dn string, port int) (*net.TCPConn, byte, error) {
	ips, _ := net.LookupIP(dn)

	for _, ip := range ips {
		if ipv4 := ip.To4(); ipv4 != nil {
			peer, reply, err := clientectIPv4(ipv4, port)
			if err == nil {
				return peer, reply, err
			}
		}
	}

	return nil, HOST_UNREACHABLE, nil
}

func sendCommandReply(client *net.TCPConn, reply byte) error {
	replyMsg := []byte{
		VER, reply, RSV, TYPEipv4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	}

	client.Write(replyMsg)

	return nil
}

func transferData(client *net.TCPConn, peer *net.TCPConn) {
	var wg sync.WaitGroup
	wg.Add(2)

	go copyData(client, peer, &wg)
	go copyData(peer, client, &wg)

	wg.Wait()
}

func copyData(dest *net.TCPConn, src *net.TCPConn, wg *sync.WaitGroup) {
	defer wg.Done()
	defer dest.Close()

	io.Copy(dest, src)
}
