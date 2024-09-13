package main

import (
	"encoding/json"
	"filetransfer/utils"
	"fmt"
	"io"
	"net"
	"os"
)

const LENGTH_BUFFER int = 4096

func printSpeed(checker SpeedChecker, filename string) {
	aspeed := checker.getAverageSpeed()
	pspeed := checker.getPartSpeed()
	fmt.Print(
		"\nfile: ", filename, "\n",
		"part speed: ", pspeed/1024, "kb/s\n",
		"average speed: ", aspeed/1024, "kb/s\n\n",
	)
}

func handleConnection(conn net.Conn) {
	defer conn.Close()

	var checker SpeedChecker
	checker.init(3)

	status := utils.UploadStatus{
		Status: utils.FAILED,
	}
	encodedStatus, err := json.Marshal(status)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		utils.Send(conn, encodedStatus)
		return
	}

	var header utils.FileHeader
	buf := make([]byte, LENGTH_BUFFER*2)

	n, err := utils.Receive(conn, buf)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		utils.Send(conn, encodedStatus)
		return
	}

	err = json.Unmarshal(buf[:n], &header)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		utils.Send(conn, encodedStatus)
		return
	}

	file, err := os.Create("uploads/" + header.Filename)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		utils.Send(conn, encodedStatus)
		return
	}
	defer file.Close()

	var read int64 = 0
	chunk := new(utils.FileChunk)

	for ; read < header.Size; read += int64(n) {
		n, err = utils.Receive(conn, buf)
		if err != nil {
			if err != io.EOF {
				fmt.Fprintln(os.Stderr, err)
				utils.Send(conn, encodedStatus)
				return
			}
			break
		}

		checker.addData(int64(n))
		if checker.expired() {
			printSpeed(checker, header.Filename)
			checker.reset()
		}

		err = json.Unmarshal(buf[:n], chunk)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			utils.Send(conn, encodedStatus)
			return
		}

		n, err = file.Write(chunk.Data)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			utils.Send(conn, encodedStatus)
			return
		}
	}

	printSpeed(checker, header.Filename)

	status.Status = utils.SUCCESS
	encodedStatus, _ = json.Marshal(status)

	utils.Send(conn, encodedStatus)
}

func main() {
	args := os.Args
	if len(args) < 2 {
		fmt.Fprintln(os.Stderr, "Wanted: <port>")
		return
	}

	port := ":" + args[1]
	listener, err := net.Listen("tcp", port)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return
	}

	err = os.Mkdir("uploads", 0755)
	if err != nil && !os.IsExist(err) {
		fmt.Fprintln(os.Stderr, err)
		return
	}

	defer listener.Close()
	fmt.Println("Server start...")
	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return
		}
		go handleConnection(conn)
	}
}
