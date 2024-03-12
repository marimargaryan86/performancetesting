package main

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"github.com/xanzy/go-gitlab"
	"go.uber.org/zap"
	"strings"
)

const commitTemplate = "%{title}\n\n%{description}\n\n%{co_authored_by}\n%{reviewed_by}\n%{approved_by}\nRefs: %{reference}"
const mergeRequestTemplate = ""
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

type label struct {
	name        string
	color       string
	description string
}

var sizeLabels = []label{
	{
		name:        "size::x-small",
		color:       "#009966",
		description: "An extra small pull request.",
	},
	{
		name:        "size::small",
		color:       "#EEE600",
		description: "A small pull request.",
	},
	{
		name:        "size::medium",
		color:       "#ED9121",
		description: "A medium pull request.",
	},
	{
		name:        "size::large",
		color:       "#CD5B45",
		description: "A large pull request.",
	},
	{
		name:        "size::x-large",
		color:       "#C21E56",
		description: "An extra large pull request.",
	},
}

var statusLabels = []label{
	{
		name:        "status::abandoned",
		color:       "#000000",
		description: "Item was started but then it was decided it was not worth the effort and/or not possible to do.",
	},
	{
		name:        "status::accepted",
		color:       "#009800",
		description: "An item has been reviewed and accepted to be merged.",
	},
	{
		name:        "status::blocked",
		color:       "#E11D21",
		description: "Item cannot progress as there is some form of impediment.",
	},
	{
		name:        "status::in progress",
		color:       "#CCCCCC",
		description: "An item is picked up by someone and is being worked on (but isn't ready for review).",
	},
	{
		name:        "status::review needed",
		color:       "#FBCA04",
		description: "An item is ready to be reviewed and / or ready for QA.",
	},
	{
		name:        "status::revision needed",
		color:       "#FF6600",
		description: "An item is reviewed and the reviewer deems that additional changes are required.",
	},
}

func verifyScopeLabels(client *gitlab.Client, logger *zap.SugaredLogger, p *gitlab.Project, config common.Configuration) {
	scopeLabels := make([]label, 0, len(config.Commits.Scopes))

	for l := range config.Commits.Scopes {
		scopeLabels = append(scopeLabels, label{
			name:        fmt.Sprintf("scope::%s", l),
			color:       "#009966",
			description: "",
		})
	}

	verifyLabels(client, logger, p, scopeLabels, "scope::", true)
}

func verifySizeLabels(client *gitlab.Client, logger *zap.SugaredLogger, p *gitlab.Project) {
	verifyLabels(client, logger, p, sizeLabels, "size::", true)
}

func verifyStatusLabels(client *gitlab.Client, logger *zap.SugaredLogger, p *gitlab.Project) {
	verifyLabels(client, logger, p, statusLabels, "status::", false)
}

func verifyLabels(client *gitlab.Client, logger *zap.SugaredLogger, p *gitlab.Project, labels []label, prefix string, deleteExtra bool) {
	currentLabels := make([]*gitlab.Label, 0)
	ch, g := common.Paginate(func(options gitlab.ListOptions) ([]*gitlab.Label, *gitlab.Response, error) {
		return client.Labels.ListLabels(p.ID, &gitlab.ListLabelsOptions{
			ListOptions:           options,
			IncludeAncestorGroups: func() *bool { b := true; return &b }(),
			Search:                &prefix,
		})
	})

	for l := range ch {
		currentLabels = append(currentLabels, l)
	}

	if err := g.Wait(); err != nil {
		logger.Error(err)
		return
	}

	for _, l := range labels {
		lLogger := logger.With("label", l.name)
		found := false

		for _, l2 := range currentLabels {
			if l.name == l2.Name {
				found = true

				if l.color != l2.Color || l.description != l2.Description {
					_, _, err := client.Labels.UpdateLabel(p.ID, &gitlab.UpdateLabelOptions{
						Name:        &l.name,
						Color:       &l.color,
						Description: &l.description,
					})

					if err != nil {
						lLogger.Error(err)
					} else {
						lLogger.Info("Label updated.")
					}
				}

				break
			}
		}

		if !found {
			_, _, err := client.Labels.CreateLabel(p.ID, &gitlab.CreateLabelOptions{
				Name:        &l.name,
				Color:       &l.color,
				Description: &l.description,
			})

			if err != nil {
				lLogger.Error(err)
			} else {
				lLogger.Info("Label created.")
			}
		}
	}

	if !deleteExtra {
		return
	}

DeleteLoop:
	for _, l := range currentLabels {
		lLogger := logger.With("label", l.Name)

		for _, l2 := range labels {
			if l.Name == l2.name {
				continue DeleteLoop
			}
		}

		_, err := client.Labels.DeleteLabel(p.ID, &gitlab.DeleteLabelOptions{
			Name: &l.Name,
		})

		if err != nil {
			lLogger.Error(err)
		} else {
			lLogger.Info("Label deleted.")
		}
	}
}

func verifyProjectSettings(client *gitlab.Client, logger *zap.SugaredLogger, p *gitlab.Project, config common.Configuration) {
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

	if config.UseMergeTrain {
		if p.MergeTrainsEnabled != true {
			changed.MergeTrainsEnabled = trueFlag
		}

		if p.MergePipelinesEnabled != true {
			changed.MergePipelinesEnabled = trueFlag
		}
	} else {
		if p.MergeTrainsEnabled != false {
			changed.MergeTrainsEnabled = falseFlag
		}

		if p.MergePipelinesEnabled != false {
			changed.MergePipelinesEnabled = falseFlag
		}
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

func manageMemberships(client *gitlab.Client, logger *zap.SugaredLogger, snowman *gitlab.User, loader *common.Loader, hookUrl string, hookSecret string) {
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

		var config common.Configuration

		config, err := loader.Load(p.ID)

		if err != nil {
			pLogger.Error(err)
			continue
		}

		verifyProjectSettings(client, pLogger, p, config)
		verifyApprovalRules(client, pLogger, p, snowman)
		verifyScopeLabels(client, pLogger, p, config)
		verifySizeLabels(client, pLogger, p)
		verifyStatusLabels(client, pLogger, p)

		var foundHook *gitlab.ProjectHook

		hooks, _, _ := client.Projects.ListProjectHooks(p.ID, &gitlab.ListProjectHooksOptions{})

		for _, h := range hooks {
			if strings.TrimSuffix(h.URL, "/") == strings.TrimSuffix(hookUrl, "/") {
				foundHook = h
			}
		}

		if foundHook == nil {
			enabled := func() *bool { b := true; return &b }()
			_, _, err = client.Projects.AddProjectHook(p.ID, &gitlab.AddProjectHookOptions{
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

	if err := g.Wait(); err != nil {
		logger.Error(err)
	}
}
