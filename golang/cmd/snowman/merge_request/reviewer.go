package merge_request

import (
	"errors"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"git.snowfall.se/junction/junction/golang/stdlib/sliceutil"
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

	if sliceutil.Equal(current, expected) {
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

func (mr *mergeRequest) appendBreakingChangeOwners(expected []int) ([]int, error) {
	if !mr.breaking {
		return expected, nil
	}

	for _, reviewer := range mr.configuration.Reviewers.Breaking {
		expected = append(expected, reviewer)
	}

	return expected, nil
}

type codeOwnerRule struct {
	EligibleApprovers []int
	ApprovalsRequired int
}

func decideOptimalCodeOwners(rules []*codeOwnerRule, current []int, blacklist []int) []int {
	indecisive := make([]codeOwnerRule, 0)
	expected := make([]int, len(current))

	copy(expected, current)

	for _, r := range rules {
		eligible := sliceutil.Without(r.EligibleApprovers, blacklist...)

		if len(eligible) <= r.ApprovalsRequired {
			expected = append(expected, eligible...)
		} else {
			indecisive = append(indecisive, codeOwnerRule{
				EligibleApprovers: eligible,
				ApprovalsRequired: r.ApprovalsRequired,
			})
		}
	}

	if len(expected) > 0 && len(indecisive) == 0 {
		return sliceutil.Unique(expected)
	}

	for len(indecisive) > 0 {
		eligible := make([]int, 0)
		stillIndecisive := make([]codeOwnerRule, 0)

		for _, r := range indecisive {
			found := 0
			ruleEligible := make([]int, 0)

			for _, reviewer := range r.EligibleApprovers {
				if sliceutil.In(expected, reviewer) {
					found++
				} else {
					ruleEligible = append(ruleEligible, reviewer)
				}
			}

			if found >= r.ApprovalsRequired {
				continue
			}

			eligible = append(eligible, ruleEligible...)
			stillIndecisive = append(stillIndecisive, r)
		}

		reviewer := sliceutil.MostCommon(eligible)

		if reviewer != 0 {
			expected = append(expected, reviewer)
		}

		indecisive = stillIndecisive
	}

	return sliceutil.Unique(expected)
}

func (mr *mergeRequest) appendCodeOwners(expected []int) ([]int, error) {
	state, err := mr.approvalState()

	if err != nil {
		return expected, err
	}

	rules := sliceutil.Map(state.Rules, func(t *gitlab.MergeRequestApprovalRule) *codeOwnerRule {
		return &codeOwnerRule{
			EligibleApprovers: sliceutil.Map(t.EligibleApprovers, func(t *gitlab.BasicUser) int {
				return t.ID
			}),
			ApprovalsRequired: t.ApprovalsRequired,
		}
	})

	optimal := decideOptimalCodeOwners(rules, expected, []int{mr.snowman.ID})

	expected = append(expected, optimal...)

	if len(expected) > 0 {
		return sliceutil.Unique(expected), nil
	}

	return []int{}, errors.New("unable to decide on a reviewer")
}

func (mr *mergeRequest) appendFileOwners(expected []int) ([]int, error) {
	if len(expected) > 0 {
		return expected, nil
	}

	eligible := make([]int, 0)

	for _, c := range mr.object.Changes {
		if c.NewFile {
			continue
		}

		owners, err := common.LikelyFileOwners(mr.client, mr.object.ProjectID, c.OldPath, mr.object.TargetBranch)

		if err != nil {
			return []int{}, err
		}

		for _, o := range owners {
			if o != mr.object.Author.ID && !sliceutil.In(mr.configuration.Reviewers.Blacklist, o) {
				eligible = append(eligible, o)
			}
		}
	}

	reviewer := sliceutil.MostCommon(eligible)

	if reviewer != 0 {
		return []int{reviewer}, nil
	}

	contributors, err := common.RecentContributors(mr.client, mr.object.ProjectID)

	if err != nil {
		return []int{}, err
	}

	reviewer = mr.object.Author.ID
	eligible = make([]int, 0)

	for _, contributor := range contributors {
		if contributor == mr.object.Author.ID || sliceutil.In(mr.configuration.Reviewers.Blacklist, contributor) {
			continue
		}

		eligible = append(eligible, contributor)
	}

	if len(eligible) > 0 {
		randomIndex := rand.Intn(len(eligible))
		reviewer = eligible[randomIndex]
	}

	return []int{reviewer}, nil
}

func (mr *mergeRequest) expectedReviewers() ([]int, error) {
	var err error

	reviewers := mr.currentReviewers()

	for _, callback := range []func([]int) ([]int, error){
		mr.appendFileOwners,
		mr.appendCodeOwners,
		mr.appendBreakingChangeOwners,
	} {
		reviewers, err = callback(reviewers)

		if err != nil {
			return sliceutil.Unique(reviewers), err
		}
	}

	return sliceutil.Unique(reviewers), nil
}
