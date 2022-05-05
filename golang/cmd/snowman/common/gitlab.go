package common

import (
	"github.com/xanzy/go-gitlab"
)

func LikelyFileOwners(client *gitlab.Client, projectId int, path string) ([]int, error) {
	owners := make([]int, 0)
	blame, _, err := client.RepositoryFiles.GetFileBlame(
		projectId,
		path,
		&gitlab.GetFileBlameOptions{
			Ref: func() *string { b := "main"; return &b }(),
		},
	)

	if err != nil {
		return owners, err
	}

	opts := &gitlab.ListUsersOptions{
		ListOptions: gitlab.ListOptions{
			PerPage: 100,
			Page:    1,
		},
		Active: func() *bool { b := true; return &b }(),
	}

	for {
		users, resp, err := client.Users.ListUsers(opts)

		if err != nil {
			return owners, err
		}

	BlameLoop:
		for _, b := range blame {
			authorName := normalize(b.Commit.AuthorName)
			for _, u := range users {
				if normalize(u.Name) == authorName {
					owners = append(owners, u.ID)
					continue BlameLoop
				}
			}
		}

		if resp.NextPage == 0 {
			break
		}

		opts.ListOptions.Page = resp.NextPage
	}

	return owners, nil
}

func RecentContributors(client *gitlab.Client, projectId int) ([]int, error) {
	contributors := make([]int, 0)
	allUsers := make([]*gitlab.User, 0)
	opts := &gitlab.ListUsersOptions{
		ListOptions: gitlab.ListOptions{
			PerPage: 100,
			Page:    1,
		},
		Active: func() *bool { b := true; return &b }(),
	}

	for {
		users, resp, err := client.Users.ListUsers(opts)

		if err != nil {
			return contributors, err
		}

		for _, u := range users {
			allUsers = append(allUsers, u)
		}

		if resp.NextPage == 0 {
			break
		}

		opts.ListOptions.Page = resp.NextPage
	}

	commits, _, err := client.Commits.ListCommits(
		projectId,
		&gitlab.ListCommitsOptions{
			ListOptions: gitlab.ListOptions{
				PerPage: 25,
				Page:    1,
			},
		},
	)

	if err != nil {
		return contributors, err
	}

	for _, c := range commits {
		authorName := normalize(c.AuthorName)

		for _, u := range allUsers {
			if normalize(u.Name) == authorName {
				contributors = append(contributors, u.ID)
			}
		}
	}

	return Unique(contributors), nil
}
