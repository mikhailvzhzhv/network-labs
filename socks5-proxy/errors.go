package main

import "fmt"

type HandshakeError struct {
	message string
}

func RaiseHandshakeError(message string) *HandshakeError {
	return &HandshakeError{message: message}
}

func (e *HandshakeError) Error() string {
	return fmt.Sprintf("Handshake error: %v", e.message)
}
