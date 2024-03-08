package merge_request

import (
	"git.snowfall.se/junction/junction/golang/stdlib/sliceutil"
	"github.com/xanzy/go-gitlab"
)

func (mr *mergeRequest) setAssignees() error {
	current := mr.currentAssignees()
	expected, err := mr.expectedAssignees()
	logger := mr.logger.With("assignees", expected)

	if err != nil {
		return err
	}

	if sliceutil.Equal(current, expected) {
		logger.Debug("Assignees already correct, skipping.")
		return nil
	}

	object, _, err := mr.client.MergeRequests.UpdateMergeRequest(
		mr.object.ProjectID,
		mr.object.IID,
		&gitlab.UpdateMergeRequestOptions{
			AssigneeIDs: &expected,
		},
	)

	if err != nil {
		return err
	}

	mr.object = object
	logger.Info("Assignee(s) updated.")

	return nil
}

func (mr *mergeRequest) currentAssignees() []int {
	current := make([]int, 0, len(mr.object.Assignees))

	for _, a := range mr.object.Assignees {
		current = append(current, a.ID)
	}

	return current
}

func (mr *mergeRequest) expectedAssignees() ([]int, error) {
	reviewers, _, err := mr.client.MergeRequests.GetMergeRequestReviewers(mr.object.ProjectID, mr.object.IID)

	if err != nil {
		return []int{}, err
	}

	approvalState, err := mr.approvalState()

	if err != nil {
		return []int{}, err
	}

	approvers := make([]int, 0)

	for _, rule := range approvalState.Rules {
		for _, u := range rule.ApprovedBy {
			approvers = append(approvers, u.ID)
		}
	}

	approvers = sliceutil.Unique(approvers)

	return determineAssignee(mr.object.Author.ID, mr.status(), reviewers, approvers), nil
}

func determineAssignee(author int, status string, reviewers []*gitlab.MergeRequestReviewer, approvers []int) []int {
	if status == statusAbandoned || status == statusAccepted {
		return []int{}
	}

	if status == statusInProgress {
		return []int{author}
	}

	assignees := make([]int, 0)

	if status == statusRevisionNeeded || status == statusBlocked {
		assignees = append(assignees, author)
	}

	for _, reviewer := range reviewers {
		if reviewer.State == "unreviewed" && !sliceutil.In(approvers, reviewer.User.ID) {
			assignees = append(assignees, reviewer.User.ID)
		}
	}

	return assignees
}
