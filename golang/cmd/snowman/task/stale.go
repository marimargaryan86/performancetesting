package task

import (
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"git.snowfall.se/junction/junction/golang/stdlib/sliceutil"
	"github.com/xanzy/go-gitlab"
	"go.uber.org/zap"
	"time"
)

func ManageStaleBranches(client *gitlab.Client, logger *zap.SugaredLogger, snowman *gitlab.User) {
	sixMonths := time.Now().Add(-(6 * 30 * 24 * time.Hour))

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
		mrBranches := make([]string, 0)
		mergeRequestsCh, g2 := common.Paginate(func(options gitlab.ListOptions) ([]*gitlab.MergeRequest, *gitlab.Response, error) {
			return client.MergeRequests.ListProjectMergeRequests(p.ID, &gitlab.ListProjectMergeRequestsOptions{
				ListOptions: options,
				State:       func() *string { b := "opened"; return &b }(),
			})
		})

		for mr := range mergeRequestsCh {
			mrBranches = append(mrBranches, mr.SourceBranch)
		}

		if err := g2.Wait(); err != nil {
			pLogger.Error(err)
		}

		branchesCh, g3 := common.Paginate(func(options gitlab.ListOptions) ([]*gitlab.Branch, *gitlab.Response, error) {
			return client.Branches.ListBranches(p.ID, &gitlab.ListBranchesOptions{
				ListOptions: options,
			})
		})

		for branch := range branchesCh {
			if branch.Default || branch.Protected || sliceutil.In(mrBranches, branch.Name) {
				continue
			}

			if branch.Commit.CommittedDate.After(sixMonths) {
				continue
			}

			// todo(jyggen): delete branches? 💥
		}

		if err := g3.Wait(); err != nil {
			pLogger.Error(err)
		}
	}

	if err := g.Wait(); err != nil {
		logger.Error(err)
	}
}
