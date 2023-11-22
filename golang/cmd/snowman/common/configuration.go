package common

import (
	"github.com/xanzy/go-gitlab"
	"gopkg.in/yaml.v2"
	"net/http"
	"time"
)

type ScopesConfiguration map[string][]string

type CommitsConfiguration struct {
	Scopes ScopesConfiguration `yaml:"scopes"`
	Types  []string            `yaml:"types"`
}

type ReviewersConfiguration struct {
	Blacklist []int `yaml:"blacklist"`
	Breaking  []int `yaml:"breaking"`
}

type Configuration struct {
	Commits       CommitsConfiguration   `yaml:"commits"`
	Reviewers     ReviewersConfiguration `yaml:"reviewers"`
	UseMergeTrain bool                   `yaml:"use_merge_train"`
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

func loadConfiguration(client *gitlab.Client, pid int) (Configuration, error) {
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

type cacheItem struct {
	value     Configuration
	fetchedAt time.Time
}

type Loader struct {
	cache  map[int]cacheItem
	client *gitlab.Client
	ttl    time.Duration
}

func NewLoader(client *gitlab.Client, ttl time.Duration) *Loader {
	return &Loader{
		client: client,
		ttl:    ttl,
	}
}

func (l *Loader) Load(pid int) (Configuration, error) {
	now := time.Now()
	val, found := l.cache[pid]

	if found && now.Sub(val.fetchedAt) < l.ttl {
		return val.value, nil
	}

	config, err := loadConfiguration(l.client, pid)
	l.cache[pid] = cacheItem{
		value:     config,
		fetchedAt: now,
	}

	return config, err
}
