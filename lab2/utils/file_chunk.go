package utils

type ChunkPos uint8

const (
	MID ChunkPos = iota
	END
)

type FileHeader struct {
	Filename string `json:"filename"`
	Size     int64  `json:"size"`
}

type FileChunk struct {
	Size int64  `json:"size"`
	Data []byte `json:"data"`
}
