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

type ConnectionError struct {
	message string
}

func RaiseConnectionError(message string) *ConnectionError {
	return &ConnectionError{message: message}
}

func (e *ConnectionError) Error() string {
	return fmt.Sprintf("Connection error: %v", e.message)
}
