package merge_request

import (
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"github.com/xanzy/go-gitlab"
)

func (mr *mergeRequest) setAssignees() error {
	current := mr.currentAssignees()
	expected, err := mr.expectedAssignees()
	logger := mr.logger.With("assignees", expected)

	if err != nil {
		return err
	}

	if common.Equal(current, expected) {
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
	status := mr.status()

	if status == statusAbandoned || status == statusAccepted {
		return []int{}, nil
	}

	if status == statusReviewNeeded {
		reviewers, err := mr.expectedReviewers()

		if err != nil {
			return []int{}, err
		}

		state, err := mr.approvalState()

		if err != nil {
			return []int{}, err
		}

		approvers := make([]int, 0)
		owners := make([]int, 0)

		for _, rule := range state.Rules {
			for _, u := range rule.ApprovedBy {
				approvers = append(approvers, u.ID)
			}

			if rule.RuleType == "code_owner" {
				for _, u := range rule.EligibleApprovers {
					owners = append(owners, u.ID)
				}
			}
		}

		missingApprovers := make([]int, 0)
		missingOwners := make([]int, 0)

		for _, reviewer := range reviewers {
			if common.In(approvers, reviewer) {
				continue
			}

			if common.In(owners, reviewer) {
				missingOwners = append(missingOwners, reviewer)
			} else {
				missingApprovers = append(missingApprovers, reviewer)
			}
		}

		if len(missingApprovers) > 0 {
			return missingApprovers, nil
		}

		if len(missingOwners) > 0 {
			return missingOwners, nil
		}
	}

	return []int{mr.object.Author.ID}, nil
}
