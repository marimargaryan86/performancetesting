package task

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"github.com/xanzy/go-gitlab"
	"go.uber.org/zap"
	"strings"
	"time"
)

const inactivityComment = "Hi @%s! :wave:\n\nYour merge request was closed because it has been stalled for over a month with no activity. You may reopen this merge request if it has been closed in error."

func ManageInactiveMergeRequests(client *gitlab.Client, logger *zap.SugaredLogger, snowman *gitlab.User) {
	oneMonth := time.Now().Add(-(30 * 24 * time.Hour))

	projectsCh, g := common.Paginate(func(options gitlab.ListOptions) ([]*gitlab.Project, *gitlab.Response, error) {
		return client.Projects.ListProjects(&gitlab.ListProjectsOptions{
			ListOptions:              options,
			Archived:                 func() *bool { b := false; return &b }(),
			Membership:               func() *bool { b := true; return &b }(),
			MinAccessLevel:           func() *gitlab.AccessLevelValue { b := gitlab.AccessLevelValue(40); return &b }(),
			WithMergeRequestsEnabled: func() *bool { b := true; return &b }(),
		})
	})

	for p := range projectsCh {
		pLogger := logger.With("project", p.ID, "name", p.Name)
		mergeRequestsCh, g2 := common.Paginate(func(options gitlab.ListOptions) ([]*gitlab.MergeRequest, *gitlab.Response, error) {
			return client.MergeRequests.ListProjectMergeRequests(p.ID, &gitlab.ListProjectMergeRequestsOptions{
				ListOptions: options,
				State:       func() *string { b := "opened"; return &b }(),
			})
		})

		for mr := range mergeRequestsCh {
			if mr.Draft {
				continue
			}

			mrLogger := logger.With("project", mr.ProjectID, "merge_request", mr.IID)
			lastActivity, err := determineLastActivity(client, mr, snowman.ID)

			if err != nil {
				mrLogger.Error(err)
			} else if lastActivity.Before(oneMonth) {
				if _, _, err = client.MergeRequests.UpdateMergeRequest(mr.ProjectID, mr.IID, &gitlab.UpdateMergeRequestOptions{
					StateEvent: func() *string { b := "close"; return &b }(),
				}); err != nil {
					mrLogger.Error(err)
				} else if _, _, err = client.Notes.CreateMergeRequestNote(
					mr.ProjectID,
					mr.IID,
					&gitlab.CreateMergeRequestNoteOptions{
						Body: func() *string { b := fmt.Sprintf(inactivityComment, mr.Author.Username); return &b }(),
					},
				); err != nil {
					mrLogger.Error(err)
				} else {
					mrLogger.Info("Closed due to inactivity.")
				}
			}
		}

		if err := g2.Wait(); err != nil {
			pLogger.Error(err)
		}
	}

	if err := g.Wait(); err != nil {
		logger.Error(err)
	}
}

func determineLastActivity(client *gitlab.Client, mergeRequest *gitlab.MergeRequest, snowmanId int) (time.Time, error) {
	mr, _, err := client.MergeRequests.GetMergeRequest(mergeRequest.ProjectID, mergeRequest.IID, nil)

	if err != nil {
		return time.Now(), err
	}

	lastUpdate := mr.CreatedAt

	notesCh, g := common.Paginate(func(options gitlab.ListOptions) ([]*gitlab.Note, *gitlab.Response, error) {
		return client.Notes.ListMergeRequestNotes(mergeRequest.ProjectID, mergeRequest.IID, &gitlab.ListMergeRequestNotesOptions{
			ListOptions: options,
		})
	})

	for n := range notesCh {
		if n.Author.ID == snowmanId || n.System {
			continue
		}

		if n.CreatedAt.After(*lastUpdate) {
			lastUpdate = n.CreatedAt
		}
	}

	if err = g.Wait(); err != nil {
		return *lastUpdate, err
	}

	commitsCh, g := common.Paginate(func(options gitlab.ListOptions) ([]*gitlab.Commit, *gitlab.Response, error) {
		return client.MergeRequests.GetMergeRequestCommits(mergeRequest.ProjectID, mergeRequest.IID, &gitlab.GetMergeRequestCommitsOptions{
			Page:    options.Page,
			PerPage: options.PerPage,
		})
	})

	if err != nil {
		return *lastUpdate, err
	}

	for c := range commitsCh {
		if c.CreatedAt.After(*lastUpdate) {
			lastUpdate = c.CreatedAt
		}
	}

	if err = g.Wait(); err != nil {
		return *lastUpdate, err
	}

	labelsCh, g := common.Paginate(func(options gitlab.ListOptions) ([]*gitlab.LabelEvent, *gitlab.Response, error) {
		return client.ResourceLabelEvents.ListMergeRequestsLabelEvents(mergeRequest.ProjectID, mergeRequest.IID, &gitlab.ListLabelEventsOptions{
			ListOptions: options,
		})
	})

	if err != nil {
		return *lastUpdate, err
	}

	for l := range labelsCh {
		if l.User.ID != snowmanId || strings.HasPrefix(l.Label.Name, "status::") {
			continue
		}

		if l.CreatedAt.After(*lastUpdate) {
			lastUpdate = l.CreatedAt
		}
	}

	if err = g.Wait(); err != nil {
		return *lastUpdate, err
	}

	return *lastUpdate, nil
}
