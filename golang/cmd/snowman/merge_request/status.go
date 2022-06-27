package merge_request

import (
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"strings"
)

const statusAbandoned = "status::abandoned"
const statusAccepted = "status::accepted"
const statusBlocked = "status::blocked"
const statusInProgress = "status::in progress"
const statusReviewNeeded = "status::review needed"
const statusRevisionNeeded = "status::revision needed"

func (mr *mergeRequest) expectedStatusLabel() (string, error) {
	if mr.object.State == "merged" {
		return statusAccepted, nil
	}

	if mr.object.State == "closed" {
		return statusAbandoned, nil
	}

	if mr.object.WorkInProgress {
		return statusInProgress, nil
	}

	if mr.object.Pipeline.Status == "failed" || !mr.object.BlockingDiscussionsResolved { // @todo: check who last commented
		return statusRevisionNeeded, nil
	}

	approvalState, err := mr.approvalState()

	if err != nil {
		return statusBlocked, err
	}

	approvers := make([]int, 0)

	for _, rule := range approvalState.Rules {
		for _, u := range rule.ApprovedBy {
			approvers = append(approvers, u.ID)
		}
	}

	approvers = common.Unique(approvers)
	reviewers, err := mr.expectedReviewers()

	if err != nil {
		return statusBlocked, err
	}

ReviewersLoop:
	for _, r := range reviewers {
		for _, a := range approvers {
			if r == a {
				continue ReviewersLoop
			}
		}

		return statusReviewNeeded, nil
	}

	if mr.object.HasConflicts || mr.object.MergeError != "" || mr.object.MergeStatus != "can_be_merged" {
		return statusBlocked, nil
	}

	return statusAccepted, nil
}

func (mr *mergeRequest) setStatus() error {
	status, err := mr.expectedStatusLabel()

	if err != nil {
		return err
	}

	return mr.setLabel(status)
}

func (mr *mergeRequest) status() string {
	for _, l := range mr.object.Labels {
		if strings.HasPrefix(l, "status::") {
			return l
		}
	}

	return statusBlocked
}
