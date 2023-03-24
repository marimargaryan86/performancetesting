package common

import (
	"errors"
	"fmt"
	"git.snowfall.se/junction/junction/golang/stdlib/sliceutil"
	"git.snowfall.se/junction/junction/golang/stdlib/strutil"
	"github.com/xanzy/go-gitlab"
	"golang.org/x/sync/errgroup"
	"regexp"
	"strings"
)

var allowedTitle *regexp.Regexp

func init() {
	allowedTitle = regexp.MustCompile(`^(?P<prefix>WIP: |Draft: )?(?P<title>(?P<type>build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(?:\((?P<scope>[a-z\d\-/]+)\))?(?P<breaking>!)?: (?P<description>[a-z].*[^.]))$`)
}

type CommitTitle struct {
	Description string
	IsBreaking  bool
	IsDraft     bool
	Scope       string
	Title       string
	Type        string
}

func (ct CommitTitle) String() string {
	var b strings.Builder

	if ct.IsDraft {
		b.WriteString("Draft: ")
	}

	b.WriteString(ct.Type)

	if ct.Scope != "" {
		b.WriteString(fmt.Sprintf("(%s)", ct.Scope))
	}

	if ct.IsBreaking {
		b.WriteString("!")
	}

	b.WriteString(fmt.Sprintf(": %s", ct.Description))

	return b.String()
}

func ParseCommitTitle(message string) (CommitTitle, error) {
	matches := allowedTitle.FindStringSubmatch(message)

	if matches == nil {
		return CommitTitle{}, errors.New("unable to parse commit title")
	}

	title := matches[allowedTitle.SubexpIndex("title")]

	if len(title) > 72 {
		return CommitTitle{}, errors.New("commit title is too long")
	}

	if strings.HasSuffix(title, ".") {
		return CommitTitle{}, errors.New("commit title must not end with a period")
	}

	return CommitTitle{
		Description: matches[allowedTitle.SubexpIndex("description")],
		IsBreaking:  matches[allowedTitle.SubexpIndex("breaking")] != "",
		IsDraft:     matches[allowedTitle.SubexpIndex("prefix")] != "",
		Scope:       matches[allowedTitle.SubexpIndex("scope")],
		Title:       title,
		Type:        matches[allowedTitle.SubexpIndex("type")],
	}, nil
}

func LikelyFileOwners(client *gitlab.Client, projectId int, path string, branch string) ([]int, error) {
	owners := make([]int, 0)
	blame, _, err := client.RepositoryFiles.GetFileBlame(
		projectId,
		path,
		&gitlab.GetFileBlameOptions{
			Ref: func() *string { b := branch; return &b }(),
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
			authorName := strutil.Normalize(b.Commit.AuthorName)
			for _, u := range users {
				if strutil.Normalize(u.Name) == authorName {
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
		authorName := strutil.Normalize(c.AuthorName)

		for _, u := range allUsers {
			if strutil.Normalize(u.Name) == authorName {
				contributors = append(contributors, u.ID)
			}
		}
	}

	return sliceutil.Unique(contributors), nil
}

func Paginate[T any](reqFunc func(options gitlab.ListOptions) ([]T, *gitlab.Response, error)) (chan T, *errgroup.Group) {
	ch := make(chan T)
	g := new(errgroup.Group)

	g.Go(func() error {
		return paginate(ch, reqFunc)
	})

	return ch, g
}

func paginate[T any](ch chan T, request func(options gitlab.ListOptions) ([]T, *gitlab.Response, error)) error {
	page := 0

	var items []T
	var res *gitlab.Response
	var err error

	for {
		items, res, err = request(gitlab.ListOptions{Page: page})

		if err != nil {
			break
		}

		for _, item := range items {
			ch <- item
		}

		if res.CurrentPage == res.TotalPages {
			break
		}

		page++
	}

	close(ch)

	return err
}
