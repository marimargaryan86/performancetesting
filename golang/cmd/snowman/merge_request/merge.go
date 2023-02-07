package merge_request

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"github.com/xanzy/go-gitlab"
	"net/http"
	"strings"
)

func (mr *mergeRequest) merge() error {
	if mr.object.State != "opened" || mr.status() != statusAccepted {
		mr.logger.Debug("Not in a mergeable state, skipping.")
		return nil
	}

	commitMessage := mr.object.Title + "\n\n"
	state, err := mr.approvalState()

	if err != nil {
		return err
	}

	names := make([]string, 0)
	hasSnowman := false

	for _, rule := range state.Rules {
		for _, user := range rule.ApprovedBy {
			if user.ID != mr.snowman.ID {
				names = append(names, user.Name)
			} else {
				hasSnowman = true
			}
		}
	}

	if !hasSnowman {
		return mr.approve()
	}

	for _, name := range common.Unique(names) {
		commitMessage += "Reviewed-by: " + name + "\n"
	}

	closesIssues, err := mr.closesIssues()

	if err != nil {
		return err
	}

	for _, issue := range closesIssues {
		if issue.References == nil {
			continue
		}

		commitMessage += "Closes: " + issue.References.Full + "\n"
	}

	if mr.object.References != nil {
		commitMessage += "Refs: " + mr.object.References.Full + "\n"
	}

	_, resp, err := mr.client.MergeRequests.AcceptMergeRequest(
		mr.object.ProjectID,
		mr.object.IID,
		&gitlab.AcceptMergeRequestOptions{
			MergeCommitMessage:        func() *string { s := strings.TrimSpace(commitMessage); return &s }(),
			SquashCommitMessage:       func() *string { s := strings.TrimSpace(commitMessage); return &s }(),
			Squash:                    func() *bool { b := true; return &b }(),
			ShouldRemoveSourceBranch:  func() *bool { b := true; return &b }(),
			MergeWhenPipelineSucceeds: func() *bool { b := true; return &b }(),
			SHA:                       func() *string { s := mr.object.SHA; return &s }(),
		},
	)

	if resp.StatusCode == http.StatusNotAcceptable || resp.StatusCode == http.StatusUnprocessableEntity {
		_, err = mr.client.MergeRequests.RebaseMergeRequest(
			mr.object.ProjectID,
			mr.object.IID,
		)

		mr.hasChanged = true
		mr.logger.Info("Rebased.")

		return err
	}

	if err != nil {
		return fmt.Errorf("merge: %w", err)
	}

	mr.hasChanged = true
	mr.logger.Info("Merged.")
	return nil
}
