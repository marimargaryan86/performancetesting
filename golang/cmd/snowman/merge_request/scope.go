package merge_request

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"strings"
)

const discussionScopeBody = "Hi @%s! :wave:\n\nSorry to interrupt, but your merge request title contains an invalid scope. Make sure there's no typo and that you're following the naming convention. If you believe your scope is correct, please ping one of the maintainers so they can create a scope label for you."
const discussionScopeSuffix = "invalid_scope"

func (mr *mergeRequest) validateScope() error {
	title, err := common.ParseCommitTitle(mr.object.Title)

	if err != nil {
		mr.logger.Warn("Unable to parse title, skipping.")
		return nil
	}

	changedPaths := make([]string, 0, len(mr.object.Changes))

	for _, change := range mr.object.Changes {
		changedPaths = append(changedPaths, change.OldPath)
		changedPaths = append(changedPaths, change.NewPath)
	}

	bestScope := determineBestScope(mr.configuration.Commits.Scopes, common.Unique(changedPaths))

	if title.Scope == "" && bestScope == "" {
		for _, l := range mr.object.Labels {
			if strings.HasPrefix(l, "scope::") {
				return mr.removeLabel(l)
			}
		}
		return nil
	}

	if bestScope != "" && bestScope != title.Scope {
		title.Scope = bestScope
		mr.setTitle(title.String())
	}

	projectLabels, err := mr.projectLabels()

	if err != nil {
		return err
	}

	scopeLabel := fmt.Sprintf("scope::%s", title.Scope)
	found := false

	for _, l := range projectLabels {
		if l.Name == scopeLabel {
			found = true
			break
		}
	}

	if !found {
		return mr.reportIssue(discussionScopeSuffix, fmt.Sprintf(discussionScopeBody, mr.object.Author.Username))
	}

	return mr.setLabel(scopeLabel)
}

func determineBestScope(scopes common.ScopesConfiguration, changedFiles []string) string {
	bestDepth := 0
	bestScope := ""
	depthConflict := false

	for scope, paths := range scopes {
		for _, path := range paths {
			for _, file := range changedFiles {
				if strings.HasPrefix(file, path) {
					depth := strings.Count(path, "/")
					if bestDepth < depth {
						bestDepth = depth
						bestScope = scope
						depthConflict = false
					} else if bestDepth == depth {
						depthConflict = true
					}
				}
			}
		}
	}

	if depthConflict {
		return ""
	}

	return bestScope
}
