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

type Sender struct {
	conn   net.Conn
	status *utils.UploadStatus
}

func sendFile(conn net.Conn, file *os.File) error {
	sender := Sender{conn: conn, status: new(utils.UploadStatus)}

	file_info, err := file.Stat()
	if err != nil {
		return err
	}

	var ok bool
	header := utils.FileHeader{
		Filename: file_info.Name(),
		Size:     file_info.Size(),
	}

	encodedHeader, err := json.Marshal(header)
	if err != nil {
		return err
	}

	utils.Send(sender.conn, encodedHeader)

	buf := make([]byte, LENGTH_BUFFER)
	receiveStatus(sender, buf, false)

	var chunk = new(utils.FileChunk)
	chunk.Size = int64(LENGTH_BUFFER)
	chunk.Data = make([]byte, LENGTH_BUFFER)

	for {
		n, err := file.Read(buf)
		if err != nil {
			if err != io.EOF {
				return err
			}
			break
		}

		copy(chunk.Data, buf[:n])

		encoded_chunk, err := json.Marshal(chunk)
		if err != nil {
			return err
		}

		_, err = utils.Send(sender.conn, encoded_chunk)
		if err != nil {
			return err
		}

		ok, err = receiveStatus(sender, buf, false)
		if !ok {
			fmt.Println("Failed")
			return err
		}

	}

	receiveStatus(sender, buf, true)

	return err
}

func receiveStatus(sender Sender, buf []byte, endmode bool) (bool, error) {
	n, err := utils.Receive(sender.conn, buf)
	if err != nil {
		return false, err
	}
	json.Unmarshal(buf[:n], sender.status)

	if endmode {
		switch sender.status.Status {
		case utils.SUCCESS:
			fmt.Println("Success!")

		case utils.FAILED:
			fmt.Println("Failed")
		}
	}

	if sender.status.Status == utils.FAILED {
		return false, err
	}

	return true, err
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
}
