package protoio

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"google.golang.org/protobuf/proto"
	"io"
)

type ProtoReader struct {
	r io.Reader
}

func NewProtoReader(r io.Reader) *ProtoReader {
	return &ProtoReader{
		r: r,
	}
}

func (pr *ProtoReader) ReadNext(message proto.Message) error {
	length, err := pr.NextMessageLength()

	if err != nil {
		return err
	}

	data := make([]byte, length)

	if _, err = io.ReadFull(pr.r, data); err != nil {
		return fmt.Errorf("unable to read message: %w", err)
	}

	err = proto.Unmarshal(data, message)

	if err != nil {
		return fmt.Errorf("unable to unmarshal message: %w", err)
	}

	return nil
}

func (pr *ProtoReader) NextMessageLength() (int64, error) {
	var length uint32

	lengthBytes := make([]byte, 4)

	if _, err := io.ReadFull(pr.r, lengthBytes); err != nil {
		return int64(length), err
	}

	err := binary.Read(bytes.NewBuffer(lengthBytes), binary.LittleEndian, &length)

	return int64(length), err
}
