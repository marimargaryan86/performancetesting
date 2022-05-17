package gtfs

import (
	"archive/zip"
	"encoding/csv"
	"github.com/jszwec/csvutil"
	"io"
	"os"
	"path/filepath"
	"reflect"
	"strings"
)

type flushable interface {
	Flush()
}

type Writer[T FileType] struct {
	encoder *csvutil.Encoder
	writer  *csv.Writer
}

func NewWriter[T FileType](w io.Writer) *Writer[T] {
	cw := csv.NewWriter(w)
	enc := csvutil.NewEncoder(cw)

	enc.Register(boolEncoder)
	enc.Register(durationEncoder)
	enc.Register(locationEncoder)
	enc.Register(timeEncoder)

	return &Writer[T]{
		encoder: enc,
		writer:  cw,
	}
}

func (w Writer[T]) Flush() {
	w.writer.Flush()
}

func (w Writer[T]) Write(t T) error {
	return w.encoder.Encode(t)
}

type fileWriterPair struct {
	file   *os.File
	writer interface{}
}

type ZipWriter struct {
	pairs   map[string]*fileWriterPair
	file    *os.File
	tempDir string
	zip     *zip.Writer
}

func NewZipWriter(path string) (*ZipWriter, error) {
	f, err := os.Create(path)

	if err != nil {
		return nil, err
	}

	tempDir, err := os.MkdirTemp("", "ssim-convert-")
	zw := &ZipWriter{pairs: make(map[string]*fileWriterPair), file: f, tempDir: tempDir, zip: zip.NewWriter(f)}

	if err != nil {
		return zw, err
	}

	for _, pair := range []struct {
		filename string
		factory  interface{}
	}{
		{"agency.txt", NewWriter[Agency]},
		{"calendar.txt", NewWriter[Calendar]},
		{"routes.txt", NewWriter[Route]},
		{"stops.txt", NewWriter[Stop]},
		{"stop_times.txt", NewWriter[StopTime]},
		{"trips.txt", NewWriter[Trip]},
	} {
		f, err = os.Create(filepath.Join(zw.tempDir, pair.filename))

		if err != nil {
			return zw, err
		}

		v := reflect.ValueOf(pair.factory)
		factory := v.Call([]reflect.Value{reflect.ValueOf(f)})
		zw.pairs[pair.filename] = &fileWriterPair{
			f,
			factory[0].Elem().Interface(),
		}
	}

	return zw, nil
}

func (w ZipWriter) Agency() Writer[Agency] {
	return w.pairs["agency.txt"].writer.(Writer[Agency])
}

func (w ZipWriter) Calendar() Writer[Calendar] {
	return w.pairs["calendar.txt"].writer.(Writer[Calendar])
}

func (w ZipWriter) Routes() Writer[Route] {
	return w.pairs["routes.txt"].writer.(Writer[Route])
}

func (w ZipWriter) Stops() Writer[Stop] {
	return w.pairs["stops.txt"].writer.(Writer[Stop])
}

func (w ZipWriter) StopTimes() Writer[StopTime] {
	return w.pairs["stop_times.txt"].writer.(Writer[StopTime])
}

func (w ZipWriter) Trips() Writer[Trip] {
	return w.pairs["trips.txt"].writer.(Writer[Trip])
}

func (w ZipWriter) Close() error {
	defer os.RemoveAll(w.tempDir)

	internalPath := strings.TrimSuffix(filepath.Base(w.file.Name()), filepath.Ext(w.file.Name()))

	for _, v := range w.pairs {
		v.writer.(flushable).Flush()

		stat, err := v.file.Stat()

		if err != nil {
			return err
		}

		if stat.Size() != 0 {
			header, err := zip.FileInfoHeader(stat)

			if err != nil {
				return err
			}

			header.Method = zip.Deflate
			header.Name = filepath.Join(internalPath, filepath.Base(v.file.Name()))
			headerWriter, err := w.zip.CreateHeader(header)

			if err != nil {
				return err
			}

			path := v.file.Name()
			f, err := os.Open(path)

			if err != nil {
				return err
			}

			_, err = io.Copy(headerWriter, f)

			f.Close()

			if err != nil {
				return err
			}
		}

		if err = v.file.Close(); err != nil {
			return err
		}
	}

	if err := w.zip.Close(); err != nil {
		return err
	}

	return w.file.Close()
}
