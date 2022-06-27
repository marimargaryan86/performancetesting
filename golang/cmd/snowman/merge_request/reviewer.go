package merge_request

import (
	"errors"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"github.com/xanzy/go-gitlab"
	"math/rand"
)

func (mr *mergeRequest) setReviewers() error {
	current := mr.currentReviewers()
	expected, err := mr.expectedReviewers()
	logger := mr.logger.With("reviewers", expected)

	if err != nil {
		return err
	}

	if common.Equal(current, expected) {
		logger.Debug("Reviewers already correct, skipping.")
		return nil
	}

	object, _, err := mr.client.MergeRequests.UpdateMergeRequest(
		mr.object.ProjectID,
		mr.object.IID,
		&gitlab.UpdateMergeRequestOptions{
			ReviewerIDs: &expected,
		},
	)

	if err != nil {
		return err
	}

	mr.object = object
	logger.Info("Reviewer(s) set.")

	return nil
}

func (mr *mergeRequest) currentReviewers() []int {
	current := make([]int, 0, len(mr.object.Reviewers))

	for _, a := range mr.object.Reviewers {
		current = append(current, a.ID)
	}

	return current
}

func (mr *mergeRequest) appendCodeOwners(expected []int, err error) ([]int, error) {
	if err != nil {
		return expected, err
	}

	current := mr.currentReviewers()
	indecisive := make([][]*gitlab.BasicUser, 0)
	state, err := mr.approvalState()

	if err != nil {
		return expected, err
	}

	for _, r := range state.Rules {
		if len(r.EligibleApprovers) == 1 {
			expected = append(expected, r.EligibleApprovers[0].ID)
		} else if len(r.EligibleApprovers) != 0 {
			indecisive = append(indecisive, r.EligibleApprovers)
		}
	}

	if len(expected) > 0 && len(indecisive) == 0 {
		return common.Unique(expected), nil
	}

	for len(indecisive) > 0 {
		eligible := make([]int, 0)
		stillIndecisive := make([][]*gitlab.BasicUser, 0)

	IndecisiveLoop:
		for _, reviewers := range indecisive {
			for _, reviewer := range reviewers {
				if common.In(expected, reviewer.ID) {
					continue IndecisiveLoop
				}
			}

			anyAdded := false

			for _, reviewer := range reviewers {
				if common.In(current, reviewer.ID) {
					expected = append(expected, reviewer.ID)
					anyAdded = true
				}
			}

			if !anyAdded {
				for _, reviewer := range reviewers {
					eligible = append(eligible, reviewer.ID)
				}

				stillIndecisive = append(stillIndecisive, reviewers)
			}
		}

		reviewer := common.MostCommon(eligible)

		if reviewer != 0 {
			expected = append(expected, reviewer)
		}

		indecisive = stillIndecisive
	}

	if len(expected) > 0 {
		return common.Unique(expected), nil
	}

	return []int{}, errors.New("unable to decide on a reviewer")
}

func (mr *mergeRequest) expectedReviewers() ([]int, error) {
	current := mr.currentReviewers()

	if len(current) > 0 {
		return mr.appendCodeOwners(current, nil)
	}

	eligible := make([]int, 0)

	for _, c := range mr.object.Changes {
		if c.NewFile {
			continue
		}

		owners, err := common.LikelyFileOwners(mr.client, mr.object.ProjectID, c.OldPath)

		if err != nil {
			return mr.appendCodeOwners([]int{}, err)
		}

		for _, o := range owners {
			if o != mr.object.Author.ID {
				eligible = append(eligible, o)
			}
		}
	}

	reviewer := common.MostCommon(eligible)

	if reviewer != 0 {
		return mr.appendCodeOwners([]int{reviewer}, nil)
	}

	contributors, err := common.RecentContributors(mr.client, mr.object.ProjectID)

	if err != nil {
		return mr.appendCodeOwners([]int{}, err)
	}

	reviewer = mr.object.Author.ID

	for len(contributors) > 1 && reviewer == mr.object.Author.ID {
		randomIndex := rand.Intn(len(contributors))
		reviewer = contributors[randomIndex]
	}

	return mr.appendCodeOwners([]int{reviewer}, nil)
}
