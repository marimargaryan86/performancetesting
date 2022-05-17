package protoio

import (
	"encoding/binary"
	"fmt"
	"google.golang.org/protobuf/proto"
	"io"
)

type ProtoWriter struct {
	w io.Writer
}

func NewProtoWriter(w io.Writer) *ProtoWriter {
	return &ProtoWriter{
		w: w,
	}
}

func (pw *ProtoWriter) Write(message proto.Message) error {
	wire, err := proto.Marshal(message)

	if err != nil {
		return fmt.Errorf("unable to marshal message: %w", err)
	}

	if err = binary.Write(pw.w, binary.LittleEndian, uint32(len(wire))); err != nil {
		return fmt.Errorf("unable to write length: %w", err)
	}

	if _, err = pw.w.Write(wire); err != nil {
		return fmt.Errorf("unable to write message: %w", err)
	}

	return nil
}
