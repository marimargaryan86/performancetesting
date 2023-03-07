package common

import (
	"github.com/xanzy/go-gitlab"
	"gopkg.in/yaml.v2"
	"net/http"
)

type ScopesConfiguration map[string][]string

type CommitsConfiguration struct {
	Scopes ScopesConfiguration `yaml:"scopes"`
	Types  []string            `yaml:"types"`
}

type Configuration struct {
	Commits CommitsConfiguration `yaml:"commits"`
}

func LoadConfiguration(client *gitlab.Client, pid int) (Configuration, error) {
	config := Configuration{
		Commits: CommitsConfiguration{
			Scopes: map[string][]string{},
			Types: []string{
				"build",
				"chore",
				"ci",
				"docs",
				"feat",
				"fix",
				"perf",
				"refactor",
				"revert",
				"style",
				"test",
			},
		},
	}
	p, _, err := client.Projects.GetProject(pid, &gitlab.GetProjectOptions{})

	if err != nil {
		return config, err
	}

	file, resp, err := client.RepositoryFiles.GetRawFile(p.ID, ".snowman.yml", &gitlab.GetRawFileOptions{
		Ref: func() *string { s := p.DefaultBranch; return &s }(),
	})

	if resp.StatusCode == http.StatusNotFound {
		return config, nil
	}

	if err != nil {
		return config, err
	}

	if err = yaml.Unmarshal(file, &config); err != nil {
		return config, err
	}

	return config, nil
}
