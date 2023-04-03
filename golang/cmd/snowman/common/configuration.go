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

type ReviewersConfiguration struct {
	Blacklist []int `yaml:"blacklist"`
}

type Configuration struct {
	Commits   CommitsConfiguration   `yaml:"commits"`
	Reviewers ReviewersConfiguration `yaml:"reviewers"`
}

func defaultConfiguration() Configuration {
	return Configuration{
		Commits: CommitsConfiguration{
			Scopes: make(map[string][]string, 0),
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
}

func decodeConfiguration(data []byte) (Configuration, error) {
	config := defaultConfiguration()

	if err := yaml.Unmarshal(data, &config); err != nil {
		return config, err
	}

	return config, nil
}

func LoadConfiguration(client *gitlab.Client, pid int) (Configuration, error) {
	p, _, err := client.Projects.GetProject(pid, &gitlab.GetProjectOptions{})

	if err != nil {
		return defaultConfiguration(), err
	}

	file, resp, err := client.RepositoryFiles.GetRawFile(p.ID, ".snowman.yml", &gitlab.GetRawFileOptions{
		Ref: func() *string { s := p.DefaultBranch; return &s }(),
	})

	if resp.StatusCode == http.StatusNotFound {
		return defaultConfiguration(), nil
	}

	if err != nil {
		return defaultConfiguration(), err
	}

	return decodeConfiguration(file)
}
