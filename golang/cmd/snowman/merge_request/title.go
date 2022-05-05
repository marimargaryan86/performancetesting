package merge_request

import (
	"fmt"
	"regexp"
)

const discussionTitleBody = "Hi @%s! :wave:\n\nSorry to interrupt, but your merge request title is not compliant with the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification."
const discussionTitleSuffix = "invalid_title"

var allowedTitle *regexp.Regexp

func init() {
	allowedTitle = regexp.MustCompile(`^(?P<prefix>WIP: |Draft: )?(?P<title>(?P<type>build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(?:\((?P<scope>[a-z\d-]+)\))?(?P<breaking>!)?: (?P<description>[a-z].*[^.]))$`)
}

func (mr *mergeRequest) validateTitle() error {
	if allowedTitle.MatchString(mr.object.Title) {
		mr.logger.Debug("Title matches format, skipping.")
		return nil
	}

	return mr.reportIssue(discussionTitleSuffix, fmt.Sprintf(discussionTitleBody, mr.object.Author.Username))
}
