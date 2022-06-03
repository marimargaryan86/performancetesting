package merge_request

import "testing"

func TestFollowsConventionalCommits(t *testing.T) {
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
		if v := followsConventionalCommits(table.input); v != table.expected {
			t.Errorf(`followsConventionalCommits("%s") was incorrect, got: %v, want: %v.`, table.input, v, table.expected)
		}
	}
}

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
