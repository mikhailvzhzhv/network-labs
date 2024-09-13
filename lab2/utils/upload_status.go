package utils

type status uint8

const (
	SUCCESS status = iota
	FAILED
)

type UploadStatus struct {
	Status status `json:"status"`
}
