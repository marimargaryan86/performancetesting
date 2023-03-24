package merge_request

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"github.com/xanzy/go-gitlab"
	"go.uber.org/zap"
	"strings"
)

const discussionPrefix = "snowman"

type cache struct {
	approvalState *gitlab.MergeRequestApprovalState
}

type mergeRequest struct {
	cache         *cache
	client        *gitlab.Client
	configuration common.Configuration
	hasChanged    bool
	logger        *zap.SugaredLogger
	object        *gitlab.MergeRequest
	snowman       *gitlab.User
}

func (mr *mergeRequest) approvalState() (*gitlab.MergeRequestApprovalState, error) {
	var err error

	if mr.cache.approvalState == nil {
		mr.cache.approvalState, _, err = mr.client.MergeRequestApprovals.GetApprovalState(
			mr.object.ProjectID,
			mr.object.IID,
		)
	}

	return mr.cache.approvalState, err
}

func (mr *mergeRequest) closesIssues() ([]*gitlab.Issue, error) {
	all := make([]*gitlab.Issue, 0)
	opts := &gitlab.GetIssuesClosedOnMergeOptions{
		PerPage: 100,
		Page:    1,
	}

	for {
		issues, resp, err := mr.client.MergeRequests.GetIssuesClosedOnMerge(
			mr.object.ProjectID,
			mr.object.IID,
			opts,
		)

		if err != nil {
			return all, nil
		}

		all = append(all, issues...)

		if resp.NextPage == 0 {
			break
		}

		opts.Page = resp.NextPage
	}

	for i, issue := range all {
		newIssue, _, err := mr.client.Issues.GetIssue(issue.ProjectID, issue.IID)

		if err != nil {
			return all, err
		}

		all[i] = newIssue
	}

	return all, nil
}

func (mr *mergeRequest) discussions() ([]*gitlab.Discussion, error) {
	all := make([]*gitlab.Discussion, 0)
	opts := &gitlab.ListMergeRequestDiscussionsOptions{
		PerPage: 100,
		Page:    1,
	}

	for {
		discussions, resp, err := mr.client.Discussions.ListMergeRequestDiscussions(
			mr.object.ProjectID,
			mr.object.IID,
			opts,
		)

		if err != nil {
			return all, nil
		}

		all = append(all, discussions...)

		if resp.NextPage == 0 {
			break
		}

		opts.Page = resp.NextPage
	}

	return all, nil
}

func (mr *mergeRequest) projectLabels() ([]*gitlab.Label, error) {
	labels := make([]*gitlab.Label, 0)
	ch, g := common.Paginate(func(options gitlab.ListOptions) ([]*gitlab.Label, *gitlab.Response, error) {
		return mr.client.Labels.ListLabels(mr.object.ProjectID, &gitlab.ListLabelsOptions{
			ListOptions: options,
		})
	})

	for l := range ch {
		labels = append(labels, l)
	}

	return labels, g.Wait()
}

func (mr *mergeRequest) reportIssue(issue string, body string) error {
	logger := mr.logger.With("issue", issue)
	discussions, err := mr.discussions()

	if err != nil {
		return err
	}

	identifier := fmt.Sprintf("<!-- %s:%s -->", discussionPrefix, issue)

	for _, discussion := range discussions {
		for _, note := range discussion.Notes {
			if note.Resolved {
				continue
			}

			if strings.Contains(note.Body, identifier) {
				logger.Debug("Issue already reported, skipping.")
				return nil
			}
		}
	}

	fullBody := fmt.Sprintf("%s\n\n%s", body, identifier)
	_, _, err = mr.client.Discussions.CreateMergeRequestDiscussion(
		mr.object.ProjectID,
		mr.object.IID,
		&gitlab.CreateMergeRequestDiscussionOptions{
			Body: &fullBody,
		},
	)

	if err != nil {
		return err
	}

	mr.hasChanged = true
	logger.Info("Issue reported.")

	return nil
}

func (mr *mergeRequest) hasLabel(label string) bool {
	for _, l := range mr.object.Labels {
		if l == label {
			return true
		}
	}

	return false
}

func (mr *mergeRequest) removeLabel(label string) error {
	logger := mr.logger.With("label", label)

	if !mr.hasLabel(label) {
		logger.Debug("Label already removed, skipping.")
		return nil
	}

	object, _, err := mr.client.MergeRequests.UpdateMergeRequest(
		mr.object.ProjectID,
		mr.object.IID,
		&gitlab.UpdateMergeRequestOptions{
			RemoveLabels: &gitlab.Labels{label},
		},
	)

	if err != nil {
		return err
	}

	mr.object = object
	mr.hasChanged = true
	logger.Info("Label removed.")

	return nil
}

func (mr *mergeRequest) setLabel(label string) error {
	logger := mr.logger.With("label", label)

	if mr.hasLabel(label) {
		logger.Debug("Label already added, skipping.")
		return nil
	}

	object, _, err := mr.client.MergeRequests.UpdateMergeRequest(
		mr.object.ProjectID,
		mr.object.IID,
		&gitlab.UpdateMergeRequestOptions{
			AddLabels: &gitlab.Labels{label},
		},
	)

	if err != nil {
		return err
	}

	mr.object = object
	mr.hasChanged = true
	logger.Info("Label added.")

	return nil
}

func (mr *mergeRequest) setTitle(title string) error {
	logger := mr.logger.With("title", title)

	object, _, err := mr.client.MergeRequests.UpdateMergeRequest(
		mr.object.ProjectID,
		mr.object.IID,
		&gitlab.UpdateMergeRequestOptions{
			Title: &title,
		},
	)

	if err != nil {
		return err
	}

	mr.object = object
	mr.hasChanged = true
	logger.Info("Title changed.")

	return nil
}

func (mr *mergeRequest) approve() error {
	_, _, err := mr.client.MergeRequestApprovals.ApproveMergeRequest(
		mr.object.ProjectID,
		mr.object.IID,
		&gitlab.ApproveMergeRequestOptions{
			SHA: &mr.object.SHA,
		},
	)

	if err != nil {
		return err
	}

	mr.hasChanged = true

	return nil
}
