package merge_request

import (
	"fmt"
)

const commentBreakingBody = "Hi @%s! :wave:\n\nYou have indicated that your merge request contains breaking changes. Please make sure that you've identified all affected dependents and inform them accordingly. This includes both first and third party dependents.\n\nAs a general note, it's always favourable to keep backward compatibility where possible and design APIs in such a way that future changes can more easily be made in a non-breaking way.\n\nIn accordance with [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), it's also a good idea to add a `BREAKING CHANGE:` footer for each breaking change to your merge request description that further describes the breaking change (e.g. `BREAKING CHANGE: foo is no longer an accepted type`). This will enable both reviewers and other developers to quickly know what the breaking changes are."
const commentBreakingSuffix = "breaking_change"

func (mr *mergeRequest) informBreakingChanges() error {
	if !mr.breaking {
		return nil
	}

	return mr.postComment(commentBreakingSuffix, fmt.Sprintf(commentBreakingBody, mr.object.Author.Username))
}
