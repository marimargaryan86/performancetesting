package strutil

import (
	"testing"
)

func TestNormalize(t *testing.T) {
	if v := Normalize("\u0440ython"); v != "\u0070ython" {
		t.Errorf(`Normalize("\u0440ython") was incorrect, got: %s, want: "python".`, v)
	}
}
