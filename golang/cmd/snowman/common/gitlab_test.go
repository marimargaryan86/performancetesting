package common

import "testing"

func TestParseCommitTitle(t *testing.T) {
	for _, table := range []struct {
		input    string
		expected bool
	}{
		{"foobar", false},
		{"feat: allow provided config object to extend other configs", true},
		{"feat!: send an email to the customer when a product is shipped", true},
		{"feat(api)!: send an email to the customer when a product is shipped", true},
		{"chore!: drop support for Node 6", true},
		{"docs: correct spelling of CHANGELOG", true},
		{"feat(lang): add Polish language", true},
	} {
		if _, v := ParseCommitTitle(table.input); (v == nil) != table.expected {
			t.Errorf(`ParseCommitTitle("%s") was incorrect, got: %v, want: %v.`, table.input, v == nil, table.expected)
		}
	}
}

func TestCommitTitleString(t *testing.T) {
	for _, message := range []string{
		"feat: allow provided config object to extend other configs",
		"feat!: send an email to the customer when a product is shipped",
		"feat(api)!: send an email to the customer when a product is shipped",
		"chore!: drop support for Node 6",
		"Draft: docs: correct spelling of CHANGELOG",
		"Draft: feat(lang): add Polish language",
	} {
		if commitTitle, _ := ParseCommitTitle(message); commitTitle.String() != message {
			t.Errorf(`string of ParseCommitTitle("%s") was incorrect, got: %s, want: %s.`, message, commitTitle.String(), message)
		}
	}
}
