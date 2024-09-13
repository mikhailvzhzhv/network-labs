package utils

import (
	"encoding/binary"
	"io"
	"net"
)

const INT_SIZE int = 4

func Send(conn net.Conn, message []byte) (int, error) {
	ibuf := intToBytes(len(message))
	n, err := conn.Write(ibuf)
	if err != nil {
		return n, err
	}
	n, err = conn.Write(message)

	return n, err
}

func Receive(conn net.Conn, encoded_data []byte) (int, error) {
	ibuf := make([]byte, INT_SIZE)
	n, err := conn.Read(ibuf)
	if err != nil {
		if err != io.EOF {
			return n, err
		}
	}

	length := bytesToInt(ibuf)

	if length == 0 {
		return n, err
	}

	read := 0
	for read < int(length) {
		n, err = conn.Read(encoded_data[read:length])
		read += n
	}

	return read, err
}

func intToBytes(length int) []byte {
	ibuf := make([]byte, INT_SIZE)
	binary.BigEndian.PutUint32(ibuf, uint32(length))
	return ibuf
}

func bytesToInt(ibuf []byte) uint32 {
	return binary.BigEndian.Uint32(ibuf)
}
