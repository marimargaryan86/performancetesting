package common

import "testing"

func TestParseCommitTitle(t *testing.T) {
	for _, tc := range []struct {
		input string
		want  bool
	}{
		{"foobar", false},
		{"feat: allow provided config object to extend other configs", true},
		{"feat!: send an email to the customer when a product is shipped", true},
		{"feat(api)!: send an email to the customer when a product is shipped", true},
		{"chore!: drop support for Node 6", true},
		{"docs: correct spelling of CHANGELOG", true},
		{"feat(lang): add Polish language", true},
	} {
		t.Run(tc.input, func(t *testing.T) {
			if _, got := ParseCommitTitle(tc.input); (got == nil) != tc.want {
				t.Errorf("got %v; want %v", got, tc.want)
			}
		})
	}
}

func TestCommitTitleString(t *testing.T) {
	for _, want := range []string{
		"feat: allow provided config object to extend other configs",
		"feat!: send an email to the customer when a product is shipped",
		"feat(api)!: send an email to the customer when a product is shipped",
		"chore!: drop support for Node 6",
		"Draft: docs: correct spelling of CHANGELOG",
		"Draft: feat(lang): add Polish language",
	} {
		t.Run(want, func(t *testing.T) {
			if commitTitle, _ := ParseCommitTitle(want); commitTitle.String() != want {
				t.Errorf("got %s; want %s", commitTitle.String(), want)
			}
		})
	}
}
