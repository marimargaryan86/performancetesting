# ssim-convert.go

There are two JSON files included using `//go:embed airports.json` and `//go:embed airlines.json`

`airports.json` has Airports, 9,083 of them as of November 2022.
`airlines.json` is a very simple list of the 2-character AirlineDesignator code that we want to include in the Scheduler.
As of November 2022, `ssim-convert.go` can create 787 separate ZIP files but we only use 47 of them, so if the code is not in this list, it is skipped.
