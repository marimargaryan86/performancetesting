package main

import (
	"github.com/xanzy/go-gitlab"
	"go.uber.org/zap"
	"strings"
)

const commitTemplate = "%{title}"
const mergeRequestTemplate = "# Merge Request\n\n## What does this MR do?\n\n## Related Issues\n"
const suggestionCommitMessage = "fix: apply review suggestions"

func verifyApprovalRules(client *gitlab.Client, logger *zap.SugaredLogger, p *gitlab.Project, snowman *gitlab.User) {
	rules, _, err := client.Projects.GetProjectApprovalRules(p.ID, &gitlab.GetProjectApprovalRulesListsOptions{})

	if err != nil {
		logger.Error(err)
		return
	}

	hasSnowman := false

	for _, r := range rules {
		if r.Name == snowman.Username {
			hasSnowman = true
			break
		}
	}

	if hasSnowman {
		// @todo: update existing rule if needed
		return
	}

	_, _, err = client.Projects.CreateProjectApprovalRule(p.ID, &gitlab.CreateProjectLevelRuleOptions{
		Name:              &snowman.Username,
		ApprovalsRequired: func() *int { i := 1; return &i }(),
		UserIDs:           func() *[]int { i := []int{snowman.ID}; return &i }(),
	})

	if err != nil {
		logger.Error(err)
		return
	}

	logger.Info("Approval rule created.")
}

func verifyProjectSettings(client *gitlab.Client, logger *zap.SugaredLogger, p *gitlab.Project) {
	empty := gitlab.EditProjectOptions{}
	changed := gitlab.EditProjectOptions{}
	trueFlag := func() *bool { b := true; return &b }()
	falseFlag := func() *bool { b := false; return &b }()

	if p.AllowMergeOnSkippedPipeline != false {
		changed.AllowMergeOnSkippedPipeline = falseFlag
	}

	if p.AutoCancelPendingPipelines != "enabled" {
		changed.AutoCancelPendingPipelines = func() *string { s := "enabled"; return &s }()
	}

	if p.AutocloseReferencedIssues != true {
		changed.AutocloseReferencedIssues = trueFlag
	}

	if p.MergeMethod != gitlab.FastForwardMerge {
		changed.MergeMethod = func() *gitlab.MergeMethodValue { s := gitlab.FastForwardMerge; return &s }()
	}

	if p.OnlyAllowMergeIfAllDiscussionsAreResolved != true {
		changed.OnlyAllowMergeIfAllDiscussionsAreResolved = trueFlag
	}

	if p.OnlyAllowMergeIfPipelineSucceeds != true {
		_, _, err := client.RepositoryFiles.GetFileMetaData(p.ID, ".gitlab-ci.yml", &gitlab.GetFileMetaDataOptions{
			Ref: func() *string { s := p.DefaultBranch; return &s }(),
		})

		if err == nil {
			changed.OnlyAllowMergeIfPipelineSucceeds = trueFlag
		}
	}

	if p.RemoveSourceBranchAfterMerge != true {
		changed.RemoveSourceBranchAfterMerge = trueFlag
	}

	if p.ResolveOutdatedDiffDiscussions != false {
		changed.ResolveOutdatedDiffDiscussions = falseFlag
	}

	if p.MergeCommitTemplate != commitTemplate {
		changed.MergeCommitTemplate = func() *string { s := commitTemplate; return &s }()
	}

	if p.SquashCommitTemplate != commitTemplate {
		changed.SquashCommitTemplate = func() *string { s := commitTemplate; return &s }()
	}

	if p.MergeRequestsTemplate != mergeRequestTemplate {
		changed.MergeRequestsTemplate = func() *string { s := mergeRequestTemplate; return &s }()
	}

	if p.SquashOption != gitlab.SquashOptionAlways {
		changed.SquashOption = func() *gitlab.SquashOptionValue { s := gitlab.SquashOptionAlways; return &s }()
	}

	if p.SuggestionCommitMessage != suggestionCommitMessage {
		changed.SuggestionCommitMessage = func() *string { s := suggestionCommitMessage; return &s }()
	}

	if changed != empty {
		_, _, err := client.Projects.EditProject(p.ID, &changed)

		if err != nil {
			logger.Error(err)
		} else {
			logger.Info("Settings updated.")
		}
	}
}

func manageMemberships(client *gitlab.Client, logger *zap.SugaredLogger, snowman *gitlab.User, hookUrl string, hookSecret string) {
	projects, _, err := client.Projects.ListProjects(&gitlab.ListProjectsOptions{
		Archived:                 func() *bool { b := false; return &b }(),
		Membership:               func() *bool { b := true; return &b }(),
		MinAccessLevel:           func() *gitlab.AccessLevelValue { b := gitlab.AccessLevelValue(40); return &b }(),
		WithMergeRequestsEnabled: func() *bool { b := true; return &b }(),
	})

	if err != nil {
		logger.Error(err)
		return
	}

	for _, p := range projects {
		pLogger := logger.With("project", p.ID, "name", p.Name)

		verifyProjectSettings(client, pLogger, p)
		verifyApprovalRules(client, pLogger, p, snowman)

		var foundHook *gitlab.ProjectHook

		hooks, _, _ := client.Projects.ListProjectHooks(p.ID, &gitlab.ListProjectHooksOptions{})

		for _, h := range hooks {
			if strings.TrimSuffix(h.URL, "/") == strings.TrimSuffix(hookUrl, "/") {
				foundHook = h
			}
		}

		if foundHook == nil {
			enabled := func() *bool { b := true; return &b }()
			_, _, err := client.Projects.AddProjectHook(p.ID, &gitlab.AddProjectHookOptions{
				ConfidentialIssuesEvents: enabled,
				ConfidentialNoteEvents:   enabled,
				DeploymentEvents:         enabled,
				EnableSSLVerification:    enabled,
				IssuesEvents:             enabled,
				JobEvents:                enabled,
				MergeRequestsEvents:      enabled,
				NoteEvents:               enabled,
				PipelineEvents:           enabled,
				PushEvents:               enabled,
				ReleasesEvents:           enabled,
				TagPushEvents:            enabled,
				Token:                    &hookSecret,
				URL:                      &hookUrl,
				WikiPageEvents:           enabled,
			})

			if err != nil {
				pLogger.Error(err)
			} else {
				pLogger.Info("Project initialized.")
			}
		}
	}
}
