package json

import (
	"encoding/json"
	"io"
)

func Stream[T any](f io.Reader, c chan T) {
	defer close(c)

	decoder := json.NewDecoder(f)

	if _, err := decoder.Token(); err != nil {
		//s.stream <- Entry{Error: fmt.Errorf("decode opening delimiter: %w", err)}
		return
	}

	for decoder.More() {
		var value T
		if err := decoder.Decode(&value); err != nil {
			//s.stream <- Entry{Error: fmt.Errorf("decode line %d: %w", i, err)}
			return
		}
		c <- value
	}

	if _, err := decoder.Token(); err != nil {
		//s.stream <- Entry{Error: fmt.Errorf("decode closing delimiter: %w", err)}
		return
	}
}
