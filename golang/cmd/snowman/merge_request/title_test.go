package merge_request

import "testing"

func TestIsImperativePresentTense(t *testing.T) {
	for _, tc := range []struct {
		input string
		want  bool
	}{
		{"adding something", false},
		{"add something", true},
		{"something added", true},
	} {
		t.Run(tc.input, func(t *testing.T) {
			if got := isImperativePresentTense(tc.input); got != tc.want {
				t.Errorf("got %v; want %v", got, tc.want)
			}
		})

	}
}
