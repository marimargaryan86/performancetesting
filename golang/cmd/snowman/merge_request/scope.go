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

	scopeLabel := fmt.Sprintf("scope::%s", title.Scope)

	if title.Scope == "" {
		for _, l := range mr.object.Labels {
			if strings.HasPrefix(l, scopeLabel) {
				return mr.removeLabel(l)
			}
		}

		mr.logger.Debug("Label not present, skipping.")
		return nil
	}

	projectLabels, err := mr.projectLabels()

	if err != nil {
		return err
	}

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
