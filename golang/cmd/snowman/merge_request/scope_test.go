package merge_request

import (
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"testing"
)

func TestDetermineBestScope(t *testing.T) {
	scopes := common.ScopesConfiguration{
		"foobar":     []string{"foobar/"},
		"foobar/sub": []string{"foobar/sub/folder", "foobar/other/sub/folder"},
		"bazqux":     []string{"bazqux/"},
		"bazqux/sub": []string{"bazqux/sub/folder", "bazqux/other/sub/folder"},
	}

	for _, table := range []struct {
		files    []string
		expected string
	}{
		{[]string{"foobar/foobar.py"}, "foobar"},
		{[]string{"foobar/sub/folder/foobar.py"}, "foobar/sub"},
		{[]string{"foobar/foobar.py", "bazqux/other/sub/folder/bazqux.py"}, "bazqux/sub"},
		{[]string{"foobar/foobar.py", "bazqux/bazqux.py"}, ""},
		{[]string{"foobar/foobar.py", "snowfall/snowfall.py"}, "foobar"},
	} {
		if scope := determineBestScope(scopes, table.files); scope != table.expected {
			t.Errorf(`determineBestScope(%v, %v) returned the wrong scope, got: "%s", wanted: "%s".`, scopes, table.files, scope, table.expected)
		}
	}
}
