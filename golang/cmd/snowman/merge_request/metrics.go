package merge_request

import (
	"git.snowfall.se/junction/junction/golang/stdlib/sliceutil"
	"path/filepath"
	"regexp"
	"strings"
)

const sizeXSmall = "size::x-small"
const sizeSmall = "size::small"
const sizeMedium = "size::medium"
const sizeLarge = "size::large"
const sizeXLarge = "size::x-large"

var sizeExtensions []string
var sizeSpecRegex *regexp.Regexp
var sizeTestRegex *regexp.Regexp

func init() {
	sizeSpecRegex = regexp.MustCompile(`/.*\.spec\..*/i`)
	sizeTestRegex = regexp.MustCompile(`/*((T|t)est|TEST).*/`)
	sizeExtensions = []string{
		// JavaScript
		"js",
		"_js",
		"bones",
		"cjs",
		"es",
		"es6",
		"frag",
		"gs",
		"jake",
		"jsb",
		"jscad",
		"jsfl",
		"jsm",
		"jss",
		"jsx",
		"mjs",
		"njs",
		"pac",
		"sjs",
		"ssjs",
		"xsjs",
		"xsjslib",
		// JavaScript: Ecere Projects
		"epj",
		// JavaScript: JavaScript+ERB
		"erb",
		// Python
		"py",
		"cgi",
		"fcgi",
		"gyp",
		"gypi",
		"lmi",
		"py3",
		"pyde",
		"pyi",
		"pyp",
		"pyt",
		"pyw",
		"rpy",
		"smk",
		"spec",
		"tac",
		"wsgi",
		"xpy",
		// Python: Cython
		"pyx",
		"pxd",
		"pxi",
		// Python: Easybuild
		"eb",
		// Python: NumPy
		"numpy",
		"numpyw",
		"numsc",
		// Python: Python traceback
		"pytb",
		// Java
		"java",
		// Java: Java Server Pages
		"jsp",
		// TypeScript
		"ts",
		// TypeScript: TSX
		"tsx",
		// C#
		"cs",
		"cake",
		"csx",
		"linq",
		// PHP
		"php",
		"aw",
		"ctp",
		"fcgi",
		"inc",
		"php3",
		"php4",
		"php5",
		"phps",
		"phpt",
		// C++
		"cpp",
		"c++",
		"cc",
		"cp",
		"cxx",
		"h",
		"h++",
		"hh",
		"hpp",
		"hxx",
		"inc",
		"inl",
		"ino",
		"ipp",
		"re",
		"tcc",
		"tpp",
		// C
		"c",
		"cats",
		"h",
		"idc",
		// C: OpenCL
		"cl",
		"opencl",
		// C: Unified Parallel C
		"upc",
		// C: X BitMap
		"xbm",
		// C: X PixMap
		"xpm",
		"pm",
		// Shell
		"sh",
		"bash",
		"bats",
		"cgi",
		"command",
		"env",
		"fcgi",
		"ksh",
		"tmux",
		"tool",
		"zsh",
		// Shell: fish
		"fish",
		// Shell: Gentoo Ebuild
		"ebuild",
		// Shell: Gentoo Eclass
		"eclass",
		// Shell: PowerShell
		"ps1",
		"psd1",
		"psm1",
		// Shell: Tcsh
		"tcsh",
		"csh",
		// Ruby
		"rb",
		"builder",
		"eye",
		"fcgi",
		"gemspec",
		"god",
		"jbuilder",
		"mspec",
		"pluginspec",
		"podspec",
		"prawn",
		"rabl",
		"rake",
		"rbi",
		"rbuild",
		"rbw",
		"rbx",
		"ru",
		"ruby",
		"spec",
		"thor",
		"watchr",
	}
}

func (mr *mergeRequest) expectedSizeLabel() string {
	additions := float64(0)

	for _, c := range mr.object.Changes {
		if !sliceutil.In(sizeExtensions, strings.TrimPrefix(filepath.Ext(c.NewPath), ".")) {
			continue
		}

		if sizeSpecRegex.MatchString(filepath.Base(c.NewPath)) || sizeTestRegex.MatchString(filepath.Base(c.NewPath)) {
			continue
		}

		for _, line := range strings.Split(c.Diff, "\n") {
			if line[0] == '+' {
				additions++
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
		return sizes[0]
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

	return result
}

func (mr *mergeRequest) setSize() error {
	return mr.setLabel(mr.expectedSizeLabel())
}
