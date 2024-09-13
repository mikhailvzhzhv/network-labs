package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net"
	"os"

	"filetransfer/utils"
)

const LENGTH_BUFFER int = 4096

func sendFile(conn net.Conn, file *os.File) error {
	file_info, err := file.Stat()
	if err != nil {
		return err
	}

	header := utils.FileHeader{
		Filename: file_info.Name(),
		Size:     file_info.Size(),
	}

	encodedHeader, err := json.Marshal(header)
	if err != nil {
		return err
	}

	utils.Send(conn, encodedHeader)

	buf := make([]byte, LENGTH_BUFFER)
	var chunk = new(utils.FileChunk)

	for {
		n, err := file.Read(buf)
		if err != nil {
			if err != io.EOF {
				return err
			}
			break
		}

		chunk.Size = int64(n)
		chunk.Data = make([]byte, n)
		copy(chunk.Data, buf[:n])

		encoded_chunk, err := json.Marshal(chunk)
		if err != nil {
			return err
		}

		_, err = utils.Send(conn, encoded_chunk)
		if err != nil {
			return err
		}
	}

	return err
}

func receiveStatus(conn net.Conn) error {
	status := new(utils.UploadStatus)
	buf := make([]byte, LENGTH_BUFFER)
	n, err := utils.Receive(conn, buf)
	if err != nil {
		return err
	}
	json.Unmarshal(buf[:n], status)

	switch status.Status {
	case utils.SUCCESS:
		fmt.Println("Success!")

	case utils.FAILED:
		fmt.Println("Failed")
	}

	return err
}

func main() {
	args := os.Args
	if len(args) < 4 {
		fmt.Fprintln(os.Stderr, "Wanted: <ip> <port> <path to file>")
		return
	}

	ip := args[1]
	port := args[2]
	filename := args[3]
	addrs := ip + ":" + port

	conn, err := net.Dial("tcp", addrs)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return
	}
	defer conn.Close()

	file, err := os.Open(filename)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return
	}
	defer file.Close()

	err = sendFile(conn, file)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
	}

	err = receiveStatus(conn)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
}
