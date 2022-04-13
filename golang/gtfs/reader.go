package gtfs

import (
	"encoding/csv"
	"github.com/jszwec/csvutil"
	"io"
)

type Reader[T FileType] struct {
	decoder *csvutil.Decoder
}

func NewReader[T FileType](r io.Reader) (*Reader[T], error) {
	dec, err := csvutil.NewDecoder(csv.NewReader(r))

	if err != nil {
		return nil, err
	}

	dec.Register(boolDecoder)
	dec.Register(durationDecoder)
	dec.Register(timeDecoder)

	return &Reader[T]{
		decoder: dec,
	}, nil
}

func (r *Reader[T]) Next() (T, error) {
	var l T
	err := r.decoder.Decode(&l)

	return l, err
}
