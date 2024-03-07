package merge_request

import (
	"bytes"
	_ "embed"
	"git.snowfall.se/junction/junction/golang/stdlib/sliceutil"
	"github.com/xanzy/go-gitlab"
	"gopkg.in/yaml.v2"
	"path/filepath"
	"regexp"
	"strings"
)

const sizeXSmall = "size::x-small"
const sizeSmall = "size::small"
const sizeMedium = "size::medium"
const sizeLarge = "size::large"
const sizeXLarge = "size::x-large"

//go:embed languages.yml
var languagesData []byte

var languages map[string]language
var sizeExtensions []string
var sizeSpecRegex *regexp.Regexp
var sizeTestRegex *regexp.Regexp

type language struct {
	FileSystemName     *string  `yaml:"fs_name"`
	Type               string   `yaml:"type"`
	Aliases            []string `yaml:"aliases"`
	AceMode            string   `yaml:"ace_mode"`
	CodeMirrorMode     string   `yaml:"codemirror_mode"`
	CodeMirrorMimeType string   `yaml:"codemirror_mime_type"`
	Wrap               bool     `yaml:"wrap"`
	Extensions         []string `yaml:"extensions"`
	Filenames          []string `yaml:"filenames"`
	Interpreters       []string `yaml:"interpreters"`
	LanguageId         int      `yaml:"language_id"`
	Color              string   `yaml:"color"`
	TextMateScope      string   `yaml:"tm_scope"`
	Group              string   `yaml:"group"`
}

func init() {
	sizeSpecRegex = regexp.MustCompile(`(?i).*\.spec\..*`)
	sizeTestRegex = regexp.MustCompile(`.*((T|t)est|TEST).*`)
	err := yaml.Unmarshal(languagesData, &languages)

	if err != nil {
		panic(err)
	}

	for _, l := range languages {
		if l.Type == "markup" || l.Type == "programming" {
			sizeExtensions = append(sizeExtensions, l.Extensions...)
		}
	}
}

func (mr *mergeRequest) expectedSizeLabel() (string, error) {
	additions := float64(0)

	for _, c := range mr.object.Changes {
		if !sliceutil.In(sizeExtensions, filepath.Ext(c.NewPath)) {
			continue
		}

		if sizeSpecRegex.MatchString(filepath.Base(c.NewPath)) || sizeTestRegex.MatchString(filepath.Base(c.NewPath)) {
			continue
		}

		if c.Diff == "" && c.NewFile {
			body, _, err := mr.client.RepositoryFiles.GetRawFile(mr.object.ProjectID, c.NewPath, &gitlab.GetRawFileOptions{
				Ref: func() *string { s := mr.object.SHA; return &s }(),
			})

			if err != nil {
				return "", err
			}

			additions += float64(bytes.Count(body, []byte{'\n'}))
		} else {
			for _, line := range strings.Split(c.Diff, "\n") {
				if len(line) > 0 && line[0] == '+' {
					additions++
				}
			}
		}
	}

	sizes := [5]string{
		sizeXSmall,
		sizeSmall,
		sizeMedium,
		sizeLarge,
		sizeXLarge,
	}

	if additions < mr.configuration.Metrics.BaseSize {
		return sizes[0], nil
	}

	index := 1
	result := sizes[index]
	currentSize := mr.configuration.Metrics.BaseSize * mr.configuration.Metrics.GrowthRate

	for additions >= currentSize {
		currentSize *= mr.configuration.Metrics.GrowthRate
		index++

		if index == len(sizes) {
			break
		}

		result = sizes[index]
	}

	return result, nil
}

func (mr *mergeRequest) setSize() error {
	label, err := mr.expectedSizeLabel()

	if err != nil {
		return err
	}

	return mr.setLabel(label)
}
