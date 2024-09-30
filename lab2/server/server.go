package main

import (
	"encoding/json"
	"filetransfer/utils"
	"fmt"
	"io"
	"net"
	"os"
	"time"
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

func setStop(stop *bool) {
	*stop = true
}

func timer(checker *SpeedChecker, stop *bool, ch <-chan string) {
	sec := 3.0
	filename := <-ch
	(*checker).init(sec)

	for !*stop {
		time.Sleep(3 * time.Second)
		printSpeed(*checker, filename)
		(*checker).reset()
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close()

	status := utils.UploadStatus{
		Status: utils.FAILED,
	}
	encodedFStatus, _ := json.Marshal(status)
	status.Status = utils.SUCCESS
	encodedSStatus, _ := json.Marshal(status)

	checker := new(SpeedChecker)
	var stop bool = false
	defer setStop(&stop)

	ch := make(chan string)
	go timer(checker, &stop, ch)

	var header utils.FileHeader
	buf := make([]byte, LENGTH_BUFFER*2)

	n, err := utils.Receive(conn, buf)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		utils.Send(conn, encodedFStatus)
		return
	}

	err = json.Unmarshal(buf[:n], &header)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		utils.Send(conn, encodedFStatus)
		return
	}
	utils.Send(conn, encodedSStatus)

	ch <- header.Filename

	file, err := os.Create("uploads/" + header.Filename)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		utils.Send(conn, encodedFStatus)
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
				utils.Send(conn, encodedFStatus)
				return
			}
			break
		}
		_, err = utils.Send(conn, encodedSStatus)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return
		}
		checker.addData(int64(n))

		err = json.Unmarshal(buf[:n], chunk)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			utils.Send(conn, encodedFStatus)
			return
		}

		n, err = file.Write(chunk.Data)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			utils.Send(conn, encodedFStatus)
			return
		}
	}

	utils.Send(conn, encodedSStatus)
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
