package merge_request

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"testing"
)

func TestDetermineBestScope(t *testing.T) {
	scopes := common.ScopesConfiguration{
		"foobar":      []string{"foobar"},
		"foobar/sub":  []string{"foobar/sub/folder", "foobar/other/sub/folder"},
		"foobar/sub2": []string{"foobar/sub2/folder", "foobar/other/sub2/folder"},
		"bazqux":      []string{"bazqux"},
		"bazqux/sub":  []string{"bazqux/sub/folder", "bazqux/other/sub/folder"},
	}

	for _, tc := range []struct {
		files []string
		want  string
	}{
		{[]string{"foobar/foobar.py"}, "foobar"},
		{[]string{"foobar/sub/folder/foobar.py"}, "foobar/sub"},
		{[]string{"foobar/foobar.py", "bazqux/other/sub/folder/bazqux.py"}, ""},
		{[]string{"foobar/foobar.py", "bazqux/bazqux.py"}, ""},
		{[]string{"foobar/foobar.py", "foobar/foobar2.py", "snowfall/snowfall.py"}, "foobar"},
		{[]string{"foobar/sub/folder/foobar.py", "foobar/other/sub2/folder/foobar.py"}, "foobar"},
	} {
		t.Run(fmt.Sprintf("%+v", tc.files), func(t *testing.T) {
			if got := determineBestScope(scopes, tc.files); got != tc.want {
				t.Errorf("got %s; want %s", got, tc.want)
			}
		})
	}
}
