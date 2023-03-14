package merge_request

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"git.snowfall.se/junction/junction/golang/stdlib/sliceutil"
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

	bestScope := determineBestScope(mr.configuration.Commits.Scopes, sliceutil.Unique(changedPaths))

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
	var possibleScopes []string
	hasMatchedScopes := false

	for _, file := range changedFiles {
		matchedScopes := make([]string, 0, len(scopes))

		for scope, paths := range scopes {
			for _, path := range paths {
				if strings.HasPrefix(file, path) {
					matchedScopes = append(matchedScopes, scope)
					break
				}
			}
		}

		if len(matchedScopes) == 0 {
			continue
		}

		if hasMatchedScopes {
			newPossibleScopes := make([]string, 0, len(scopes))
			for _, scope := range matchedScopes {
				if sliceutil.In(possibleScopes, scope) {
					newPossibleScopes = append(newPossibleScopes, scope)
				}
			}

			possibleScopes = newPossibleScopes
		} else {
			hasMatchedScopes = true
			possibleScopes = make([]string, len(matchedScopes))
			copy(possibleScopes, matchedScopes)
		}
	}

	bestDepth := -1
	bestScope := ""
	depthConflict := false

	for _, scope := range possibleScopes {
		for _, path := range scopes[scope] {
			depth := strings.Count(path, "/")
			if bestDepth < depth {
				bestDepth = depth
				bestScope = scope
				depthConflict = false
			} else if bestDepth == depth && bestScope != scope {
				depthConflict = true
			}
		}
	}

	if depthConflict {
		return ""
	}

	return bestScope
}
