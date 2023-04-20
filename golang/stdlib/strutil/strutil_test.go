package strutil

import (
	"testing"
)

func TestNormalize(t *testing.T) {
	if got := Normalize("\u0440ython"); got != "\u0070ython" {
		t.Errorf("got %s; want %s", got, "\u0070ython")
	}
}
