package main

import (
	"flag"
	"log"
	"os"
	"strconv"

	v1alpha "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"
	"github.com/uber/h3-go/v4"
)

func check(err error) {
	if err != nil {
		panic(err)
	}
}

type Env struct {
	outputPath string
	dataPath   string
}

func getCommandLineParams() (string, string, error) {
	// Uses flags to read input_dir, output_dir from command line params.
	// Any error, prints error and returns nil, nil, error
	var inputDirP = flag.String("input-dir", "", "Input directory containing the GTFS ZIO file")
	var outputDirP = flag.String("output-dir", "", "Output directory where the JSON files will be placed")
	flag.Parse()

	if *inputDirP == "" || *outputDirP == "" {
		log.Fatalln("No input or output directory specified")
	}
	checkDataDirectory(inputDirP)
	check(os.MkdirAll(*outputDirP, 0755))
	checkDataDirectory(outputDirP)
	return *inputDirP, *outputDirP, nil
}

func checkDataDirectory(checkDirectory *string) {
	// TODO extract to single common file ??

	file, err := os.Stat(*checkDirectory)
	if err != nil {
		log.Fatalln("Fatal: directory: ", *checkDirectory, " Error: ", err)
	}
	if !file.IsDir() {
		log.Fatalln("Fatal:  directory: ", *checkDirectory, " Not a directory")
	}
}

func getParams() Env {
	inputDir, outputDir, err := getCommandLineParams()
	if err != nil {
		panic(err)
	}
	return Env{
		outputPath: outputDir,
		dataPath:   inputDir,
	}
}

func maxU32(a uint32, b uint32) uint32 {
	if a > b {
		return a
	}
	return b
}

func getGeoIdentifier(coords *v1alpha.Coordinates) uint64 {
	return uint64(h3.LatLngToCell(h3.LatLng{
		Lng: coords.Longitude,
		Lat: coords.Latitude,
	}, 9))
}

func uint32ToByte(i uint32) []byte {
	return []byte(strconv.FormatUint(uint64(i), 10))
}
