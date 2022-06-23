package merge_request

import "testing"

func TestIsImperativePresentTense(t *testing.T) {
	for _, table := range []struct {
		input    string
		expected bool
	}{
		{"adding something", false},
		{"add something", true},
		{"something added", true},
	} {
		if v := isImperativePresentTense(table.input); v != table.expected {
			t.Errorf(`isImperativePresentTense("%s") was incorrect, got: %v, want: %v.`, table.input, v, table.expected)
		}
	}
}
