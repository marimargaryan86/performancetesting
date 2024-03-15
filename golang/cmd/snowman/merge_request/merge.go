package merge_request

import (
	"fmt"
	"github.com/xanzy/go-gitlab"
	"net/http"
)

func (mr *mergeRequest) merge() error {
	state, err := mr.approvalState()
	hasSnowman := false

	for _, rule := range state.Rules {
		for _, user := range rule.ApprovedBy {
			if user.ID == mr.snowman.ID {
				hasSnowman = true
				break
			}
		}
	}

	if mr.object.State != "opened" || mr.status() != statusAccepted {
		mr.logger.Debug("Not in a mergeable state, skipping.")

		if mr.status() != statusAccepted && hasSnowman {
			return mr.unapprove()
		}
		return nil
	}

	if !hasSnowman {
		if err = mr.approve(); err != nil {
			return err
		}
	}

	var resp *gitlab.Response

	if mr.configuration.UseMergeTrain {
		_, resp, err = mr.client.MergeTrains.GetMergeRequestOnAMergeTrain(mr.object.ProjectID, mr.object.IID)

		if resp.StatusCode != http.StatusNotFound {
			return nil
		}

		_, resp, err = mr.client.MergeTrains.AddMergeRequestToMergeTrain(
			mr.object.ProjectID,
			mr.object.IID,
			&gitlab.AddMergeRequestToMergeTrainOptions{
				SHA:                  func() *string { s := mr.object.SHA; return &s }(),
				Squash:               func() *bool { b := true; return &b }(),
				WhenPipelineSucceeds: func() *bool { b := true; return &b }(),
			},
		)

		if err != nil {
			return fmt.Errorf("merge train: %w", err)
		}
	} else {
		_, resp, err = mr.client.MergeRequests.AcceptMergeRequest(
			mr.object.ProjectID,
			mr.object.IID,
			&gitlab.AcceptMergeRequestOptions{
				Squash:                    func() *bool { b := true; return &b }(),
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
	}

	mr.hasChanged = true
	mr.logger.Info("Merged.")
	return nil
}
