package merge_request

import (
	"fmt"
	"regexp"
	"strings"
)

const discussionForbiddenBody = "Hi @%s! :wave:\n\nSorry to interrupt, but your merge request title is not in imperative present tense (e.g. it should be `add` and not `adds`, `adding` or `added`)."
const discussionForbiddenSuffix = "forbidden_word"
const discussionTitleBody = "Hi @%s! :wave:\n\nSorry to interrupt, but your merge request title is not compliant with the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification."
const discussionTitleSuffix = "invalid_title"

var allowedTitle *regexp.Regexp
var forbiddenWords []string

func init() {
	allowedTitle = regexp.MustCompile(`^(?P<prefix>WIP: |Draft: )?(?P<title>(?P<type>build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(?:\((?P<scope>[a-z\d\-/]+)\))?(?P<breaking>!)?: (?P<description>[a-z].*[^.]))$`)
	forbiddenWords = []string{
		"adds", "adding", "added",
		"allows", "allowing", "allowed",
		"amends", "amending", "amended",
		"bumps", "bumping", "bumped",
		"calculates", "calculating", "calculated",
		"changes", "changing", "changed",
		"cleans", "cleaning", "cleaned",
		"commits", "committing", "committed",
		"corrects", "correcting", "corrected",
		"creates", "creating", "created",
		"darkens", "darkening", "darkened",
		"disables", "disabling", "disabled",
		"displays", "displaying", "displayed",
		"drys", "drying", "dryed",
		"ends", "ending", "ended",
		"enforces", "enforcing", "enforced",
		"enqueues", "enqueuing", "enqueued",
		"extracts", "extracting", "extracted",
		"finishes", "finishing", "finished",
		"fixes", "fixing", "fixed",
		"formats", "formatting", "formatted",
		"guards", "guarding", "guarded",
		"handles", "handling", "handled",
		"hides", "hiding", "hid",
		"increases", "increasing", "increased",
		"ignores", "ignoring", "ignored",
		"implements", "implementing", "implemented",
		"improves", "improving", "improved",
		"keeps", "keeping", "kept",
		"kills", "killing", "killed",
		"makes", "making", "made",
		"merges", "merging", "merged",
		"moves", "moving", "moved",
		"permits", "permitting", "permitted",
		"prevents", "preventing", "prevented",
		"pushes", "pushing", "pushed",
		"rebases", "rebasing", "rebased",
		"refactors", "refactoring", "refactored",
		"removes", "removing", "removed",
		"renames", "renaming", "renamed",
		"reorders", "reordering", "reordered",
		"replaces", "replacing", "replaced",
		"requires", "requiring", "required",
		"restores", "restoring", "restored",
		"reverts", "reverting", "reverted",
		"sends", "sending", "sent",
		"sets", "setting",
		"separates", "separating", "separated",
		"shows", "showing", "showed",
		"skips", "skipping", "skipped",
		"sorts", "sorting", "sorted",
		"speeds", "speeding", "sped",
		"starts", "starting", "started",
		"supports", "supporting", "supported",
		"takes", "taking", "took",
		"tests", "testing", "tested",
		"truncates", "truncating", "truncated",
		"updates", "updating", "updated",
		"uses", "using", "used",
	}
}

func (mr *mergeRequest) validateTitle() error {
	if !followsConventionalCommits(mr.object.Title) {
		return mr.reportIssue(discussionTitleSuffix, fmt.Sprintf(discussionTitleBody, mr.object.Author.Username))
	}

	matches := allowedTitle.FindStringSubmatch(mr.object.Title)
	description := matches[allowedTitle.SubexpIndex("description")]

	if !isImperativePresentTense(description) {
		return mr.reportIssue(discussionForbiddenSuffix, fmt.Sprintf(discussionForbiddenBody, mr.object.Author.Username))
	}

	mr.logger.Debug("Title matches format, skipping.")
	return nil
}

func isImperativePresentTense(sentence string) bool {
	words := strings.SplitN(sentence, " ", 2)

	for _, forbidden := range forbiddenWords {
		if words[0] == forbidden {
			return false
		}
	}

	return true
}

func followsConventionalCommits(title string) bool {
	return allowedTitle.MatchString(title)
}
