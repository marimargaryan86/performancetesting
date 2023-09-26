package merge_request

import (
	"git.snowfall.se/junction/junction/golang/stdlib/sliceutil"
	"github.com/xanzy/go-gitlab"
	"testing"
)

type determineAssigneeTestCase struct {
	author    int
	status    string
	reviewers []*gitlab.MergeRequestReviewer
	want      []int
}

func TestDetermineAssignee(t *testing.T) {
	testCases := []determineAssigneeTestCase{
		{
			author: 1,
			status: statusAbandoned,
			reviewers: []*gitlab.MergeRequestReviewer{
				{
					User:  &gitlab.BasicUser{ID: 2},
					State: "unreviewed",
				},
				{
					User:  &gitlab.BasicUser{ID: 3},
					State: "reviewed",
				},
			},
			want: []int{},
		},
		{
			author: 1,
			status: statusAccepted,
			reviewers: []*gitlab.MergeRequestReviewer{
				{
					User:  &gitlab.BasicUser{ID: 2},
					State: "unreviewed",
				},
				{
					User:  &gitlab.BasicUser{ID: 3},
					State: "reviewed",
				},
			},
			want: []int{},
		},
		{
			author: 1,
			status: statusInProgress,
			reviewers: []*gitlab.MergeRequestReviewer{
				{
					User:  &gitlab.BasicUser{ID: 2},
					State: "unreviewed",
				},
				{
					User:  &gitlab.BasicUser{ID: 3},
					State: "reviewed",
				},
			},
			want: []int{1},
		},
		{
			author: 1,
			status: statusRevisionNeeded,
			reviewers: []*gitlab.MergeRequestReviewer{
				{
					User:  &gitlab.BasicUser{ID: 2},
					State: "unreviewed",
				},
				{
					User:  &gitlab.BasicUser{ID: 3},
					State: "reviewed",
				},
			},
			want: []int{1, 2},
		},
		{
			author: 1,
			status: statusReviewNeeded,
			reviewers: []*gitlab.MergeRequestReviewer{
				{
					User:  &gitlab.BasicUser{ID: 2},
					State: "unreviewed",
				},
				{
					User:  &gitlab.BasicUser{ID: 3},
					State: "reviewed",
				},
			},
			want: []int{2},
		},
		{
			author: 1,
			status: statusBlocked,
			reviewers: []*gitlab.MergeRequestReviewer{
				{
					User:  &gitlab.BasicUser{ID: 2},
					State: "unreviewed",
				},
				{
					User:  &gitlab.BasicUser{ID: 3},
					State: "reviewed",
				},
			},
			want: []int{1, 2},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.status, func(t *testing.T) {
			if got := determineAssignee(tc.author, tc.status, tc.reviewers); !sliceutil.Equal(got, tc.want) {
				t.Errorf("got %v; want %v", got, tc.want)
			}
		})
	}
}
