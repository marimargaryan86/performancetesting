package merge_request

import (
	"github.com/sergi/go-diff/diffmatchpatch"
	"github.com/xanzy/go-gitlab"
	"net/url"
	"regexp"
	"strings"
)

type DiffLine struct {
	Path       string
	LineNumber int
	Text       string
}

var ignorePatterns []*regexp.Regexp
var rawIgnorePatterns = []string{
	"# noqa: ?[A-Z]+[0-9]+(?:, ?[A-Z]+[0-9]+)*",            // Flake8/Ruff
	"# shellcheck disable=(?:[A-Z0-9]+(?:-[A-Z0-9]+)?,?)+", // shellcheck
	"# type: ignore\\[[^\\]]+\\]",                          // Mypy
}

func init() {
	ignorePatterns = make([]*regexp.Regexp, 0, len(rawIgnorePatterns))

	for _, pattern := range rawIgnorePatterns {
		ignorePatterns = append(ignorePatterns, regexp.MustCompile(pattern))
	}
}

func FindLinesWithNewIgnores(gld gitlab.Diff) ([]DiffLine, error) {
	dmp := diffmatchpatch.New()
	linesWithNewIgnores := make([]DiffLine, 0)

	if gld.DeletedFile {
		return linesWithNewIgnores, nil
	}
	parts := strings.Split(gld.Diff, "\n")

	for i, part := range parts {
		if strings.HasPrefix(part, "@@") {
			parts[i] = part[0 : strings.LastIndex(part, "@@")+2]
		}
	}

	gld.Diff = strings.Join(parts, "\n")
	patches, err := dmp.PatchFromText(gld.Diff)

	if err != nil {
		return linesWithNewIgnores, err
	}

	for _, patch := range patches {
		lines := strings.Split(patch.String(), "\n")
		origLineNumber := patch.Start1
		newLineNumber := patch.Start2
		newBuffer := make([]DiffLine, 0)
		origBuffer := make([]DiffLine, 0)

		for _, line := range lines {
			if len(line) == 0 {
				continue
			}

			switch line[0] {
			case '-':
				line, err = url.QueryUnescape(line[1:])

				if err != nil {
					return linesWithNewIgnores, err
				}

				origBuffer = append(origBuffer, DiffLine{
					Path:       gld.NewPath,
					LineNumber: newLineNumber,
					Text:       line,
				})
				origLineNumber++
			case '+':
				line, err = url.QueryUnescape(line[1:])

				if err != nil {
					return linesWithNewIgnores, err
				}

				newBuffer = append(newBuffer, DiffLine{
					Path:       gld.NewPath,
					LineNumber: newLineNumber,
					Text:       line,
				})
				newLineNumber++
			default:
				if len(newBuffer) > 0 || len(origBuffer) > 0 {
					linesWithNewIgnores = append(linesWithNewIgnores, findNewIgnores(dmp, newBuffer, origBuffer)...)
					newBuffer = make([]DiffLine, 0)
					origBuffer = make([]DiffLine, 0)
				}
				origLineNumber++
				newLineNumber++
			}
		}

		if len(newBuffer) > 0 || len(origBuffer) > 0 {
			linesWithNewIgnores = append(linesWithNewIgnores, findNewIgnores(dmp, newBuffer, origBuffer)...)
		}
	}

	return linesWithNewIgnores, err
}

func findNewIgnores(dmp *diffmatchpatch.DiffMatchPatch, addedLines []DiffLine, removedLines []DiffLine) []DiffLine {
	newIgnores := make([]DiffLine, 0)
	addedLinesWithIgnores := make([]DiffLine, 0)
	addedIgnoresAsText := ""
	removedIgnoresASText := ""

	for _, a := range addedLines {
		for _, pattern := range ignorePatterns {
			if match := pattern.FindString(a.Text); match != "" {
				addedLinesWithIgnores = append(addedLinesWithIgnores, a)
				addedIgnoresAsText += match + "\n"
			}
		}
	}

	if addedIgnoresAsText == "" {
		return newIgnores
	}

	for _, r := range removedLines {
		for _, pattern := range ignorePatterns {
			if match := pattern.FindString(r.Text); match != "" {
				removedIgnoresASText += match + "\n"
			}
		}
	}

	index := 0

	for _, d := range dmp.DiffMain(removedIgnoresASText, addedIgnoresAsText, false) {
		if d.Type == diffmatchpatch.DiffInsert {
			ignores := strings.Split(strings.TrimSpace(d.Text), "\n")

			for i := range ignores {
				newIgnores = append(newIgnores, addedLinesWithIgnores[index+i])
			}
		}

		index += strings.Count(d.Text, "\n")
	}

	return newIgnores
}
