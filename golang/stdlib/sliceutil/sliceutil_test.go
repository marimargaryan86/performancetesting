package sliceutil

import "testing"

func TestEqual(t *testing.T) {
	if !Equal([]string{"foobar"}, []string{"foobar"}) {
		t.Errorf(`Equal(%v, %v) was incorrect, got: false, want: true.`, []string{"foobar"}, []string{"foobar"})
	}

	if Equal([]string{"foobar"}, []string{"bazqux"}) {
		t.Errorf(`Equal(%v, %v) was incorrect, got: true, want: false.`, []string{"foobar"}, []string{"bazqux"})
	}
}

func TestIn(t *testing.T) {
	if !In([]string{"foobar"}, "foobar") {
		t.Errorf(`In(%v, "foobar") was incorrect, got: false, want: true.`, []string{"foobar"})
	}

	if In([]string{"foobar"}, "bazqux") {
		t.Errorf(`In(%v, "bazqux") was incorrect, got: true, want: false.`, []string{"foobar"})
	}
}

func TestMostCommon(t *testing.T) {
	if v := MostCommon([]string{"foobar", "foobar", "bazqux"}); v != "foobar" {
		t.Errorf(`MostCommon(%v) was incorrect, got: "%s", want: "foobar".`, []string{"foobar", "foobar", "bazqux"}, v)
	}
}

func TestUnique(t *testing.T) {
	if v := Unique([]string{"foobar", "foobar"}); !Equal(v, []string{"foobar"}) {
		t.Errorf(`Unique(%v) was incorrect, got: %v, want: %v.`, []string{"foobar", "foobar"}, v, []string{"foobar"})
	}
}
