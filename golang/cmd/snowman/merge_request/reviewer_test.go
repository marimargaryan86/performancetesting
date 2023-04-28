package merge_request

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/stdlib/sliceutil"
	"strings"
	"testing"
)

type decideOptimalCodeOwnersTestCase struct {
	rules     []*codeOwnerRule
	current   []int
	blacklist []int
	want      []int
}

func (tc *decideOptimalCodeOwnersTestCase) String() string {
	var b strings.Builder

	for i, r := range tc.rules {
		if i != 0 {
			b.WriteString(" and ")
		}

		b.WriteString(fmt.Sprintf("rule with %d eligible and %d required approvers", len(r.EligibleApprovers), r.ApprovalsRequired))
	}

	b.WriteString(fmt.Sprintf(" and with %d current and %d blacklisted reviewers", len(tc.current), len(tc.blacklist)))

	return b.String()
}

func TestDecideOptimalCodeOwners(t *testing.T) {
	testCases := []decideOptimalCodeOwnersTestCase{
		{
			[]*codeOwnerRule{
				{
					[]int{1},
					1,
				},
			},
			[]int{},
			[]int{},
			[]int{1},
		},
		{
			[]*codeOwnerRule{
				{
					[]int{1, 2},
					1,
				},
			},
			[]int{},
			[]int{},
			[]int{1},
		},
		{
			[]*codeOwnerRule{
				{
					[]int{1},
					2,
				},
			},
			[]int{},
			[]int{},
			[]int{1},
		},
		{
			[]*codeOwnerRule{
				{
					[]int{1, 2},
					2,
				},
			},
			[]int{},
			[]int{},
			[]int{1, 2},
		},
		{
			[]*codeOwnerRule{
				{
					[]int{1, 2},
					1,
				},
			},
			[]int{},
			[]int{2},
			[]int{1},
		},
		{
			[]*codeOwnerRule{
				{
					[]int{1, 2},
					1,
				},
				{
					[]int{2, 3},
					1,
				},
			},
			[]int{},
			[]int{},
			[]int{2},
		},
		{
			[]*codeOwnerRule{
				{
					[]int{1, 2},
					1,
				},
				{
					[]int{2, 3},
					1,
				},
			},
			[]int{1},
			[]int{},
			[]int{1, 2},
		},
		{
			[]*codeOwnerRule{
				{
					[]int{1, 2, 3},
					2,
				},
			},
			[]int{1},
			[]int{},
			[]int{1, 2},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.String(), func(t *testing.T) {
			if got := decideOptimalCodeOwners(tc.rules, tc.current, tc.blacklist); !sliceutil.Equal(got, tc.want) {
				t.Errorf("got %v; want %v", got, tc.want)
			}
		})
	}
}
