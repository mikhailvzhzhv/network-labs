package main

const (
	VER   = 0x05
	AUTH  = 0x00
	CAUTH = 0x00
	// no acceptable methods were offered
	CAUTHF = 0xFF

	// address
	TYPEipv4 = 0x01
	TYPEdn   = 0x03
	CMD      = 0x01
	RSV      = 0x00

	// status
	REQUEST_GRANTED            = 0x00
	GENERAL_FAILURE            = 0x01
	CONNECTION_NOT_ALLOWED     = 0x02
	NETWORK_UNREACHABLE        = 0x03
	HOST_UNREACHABLE           = 0x04
	CONNECTION_REFUSED         = 0x05
	TTL_EXPIRED                = 0x06
	COMMAND_NOT_SUPPORTED      = 0x07
	ADDRESS_TYPE_NOT_SUPPORTED = 0x08
)
