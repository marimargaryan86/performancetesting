package gtfs

import (
	"encoding/csv"
	"github.com/jszwec/csvutil"
	"io"
	"net/url"
)

type ParserFactory func(r io.Reader) (Parser, error)

type Parser interface {
	Next() (interface{}, error)
}

type RouteParser struct {
	decoder *csvutil.Decoder
}

func NewRouteParser(r io.Reader) (Parser, error) {
	dec, err := csvutil.NewDecoder(csv.NewReader(r))

	if err != nil {
		return nil, err
	}

	dec.Register(urlDecoder)

	return &RouteParser{
		decoder: dec,
	}, nil
}

func (rp *RouteParser) Next() (interface{}, error) {
	r := Route{}
	err := rp.decoder.Decode(&r)

	return r, err
}

type StopParser struct {
	decoder *csvutil.Decoder
}

func NewStopParser(r io.Reader) (Parser, error) {
	dec, err := csvutil.NewDecoder(csv.NewReader(r))

	if err != nil {
		return nil, err
	}

	dec.Register(urlDecoder)

	return &StopParser{
		decoder: dec,
	}, nil
}

func (sp *StopParser) Next() (interface{}, error) {
	s := Stop{}
	err := sp.decoder.Decode(&s)

	return s, err
}

type StopTimeParser struct {
	decoder *csvutil.Decoder
}

func NewStopTimeParser(r io.Reader) (Parser, error) {
	dec, err := csvutil.NewDecoder(csv.NewReader(r))

	if err != nil {
		return nil, err
	}

	dec.Register(urlDecoder)

	return &StopTimeParser{
		decoder: dec,
	}, nil
}

func (stp *StopTimeParser) Next() (interface{}, error) {
	st := StopTime{}
	err := stp.decoder.Decode(&st)

	return st, err
}

type TransferParser struct {
	decoder *csvutil.Decoder
}

func NewTransferParser(r io.Reader) (Parser, error) {
	dec, err := csvutil.NewDecoder(csv.NewReader(r))

	if err != nil {
		return nil, err
	}

	dec.Register(urlDecoder)

	return &TransferParser{
		decoder: dec,
	}, nil
}

func (tp *TransferParser) Next() (interface{}, error) {
	t := Transfer{}
	err := tp.decoder.Decode(&t)

	return t, err
}

type TripParser struct {
	decoder *csvutil.Decoder
}

func NewTripParser(r io.Reader) (Parser, error) {
	dec, err := csvutil.NewDecoder(csv.NewReader(r))

	if err != nil {
		return nil, err
	}

	dec.Register(urlDecoder)

	return &TripParser{
		decoder: dec,
	}, nil
}

func (tp *TripParser) Next() (interface{}, error) {
	t := Trip{}
	err := tp.decoder.Decode(&t)

	return t, err
}

func urlDecoder(data []byte, f **url.URL) error {
	v, err := url.Parse(string(data))

	if err != nil {
		return err
	}

	*f = v

	return nil
}
