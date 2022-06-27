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

		regulars := make([]int, 0)
		owners := make([]int, 0)

		for _, rule := range state.Rules {
			for _, u := range rule.ApprovedBy {
				if rule.RuleType == "any_approver" {
					regulars = append(regulars, u.ID)
				} else {
					owners = append(owners, u.ID)
				}
			}
		}

		newRegulars := make([]int, 0)

		for _, regular := range regulars {
			if !common.In(owners, regular) {
				newRegulars = append(newRegulars, regular)
			}
		}

		regulars = newRegulars

		for _, approvers := range [][]int{
			regulars,
			owners,
		} {
			approvers = common.Unique(approvers)
			missing := make([]int, 0)

		ReviewersLoop:
			for _, r := range reviewers {
				for _, a := range approvers {
					if r == a {
						continue ReviewersLoop
					}
				}

				missing = append(missing, r)
			}

			if len(missing) > 0 {
				return missing, nil
			}
		}
	}

	return []int{mr.object.Author.ID}, nil
}
