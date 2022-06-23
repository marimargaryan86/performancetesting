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
