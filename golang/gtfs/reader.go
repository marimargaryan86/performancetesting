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
	dec.Register(locationDecoder)
	dec.Register(timeDecoder)

	dec.Map = func(field, column string, v interface{}) string {
		if _, ok := v.(uint); ok && field == "" {
			return "0"
		}

		return field
	}

	return &Reader[T]{
		decoder: dec,
	}, nil
}

func (r *Reader[T]) Next() (T, error) {
	var l T
	err := r.decoder.Decode(&l)

	return l, err
}
