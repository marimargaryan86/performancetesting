package protoio

import (
	"encoding/binary"
	"fmt"
	"google.golang.org/protobuf/proto"
	"io"
)

type ProtoWriter[T proto.Message] struct {
	w          io.Writer
	FileLength uint64
}

func NewProtoWriter[T proto.Message](w io.Writer) *ProtoWriter[T] {
	return &ProtoWriter[T]{
		w: w,
	}
}

func (pw *ProtoWriter[T]) Write(message T) error {
	wire, err := proto.Marshal(message)

	if err != nil {
		return fmt.Errorf("unable to marshal message: %w", err)
	}

	if err = binary.Write(pw.w, binary.LittleEndian, uint32(len(wire))); err != nil {
		return fmt.Errorf("unable to write length: %w", err)
	}

	bytesWrote, err := pw.w.Write(wire)
	if err != nil {
		return fmt.Errorf("unable to write message: %w", err)
	}
	if bytesWrote != len(wire) {
		return fmt.Errorf("Bytes written: %d does no match buffer length: %d", bytesWrote, len(wire))
	}
	pw.FileLength += uint64(4 + len(wire)) // 4 byte uint32 length + protobuffer

	return nil
}
