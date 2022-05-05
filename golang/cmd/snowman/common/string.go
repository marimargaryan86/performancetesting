package common

import (
	"github.com/jyggen/confusables"
	"golang.org/x/text/runes"
	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
	"strings"
	"unicode"
)

var normalizer = transform.Chain(norm.NFD, runes.Remove(runes.In(unicode.Mn)), norm.NFC)

func normalize(input string) string {
	output, _, _ := transform.String(normalizer, input)

	return confusables.Skeleton(strings.ToLower(output))
}
