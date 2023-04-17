package main

import (
	"encoding/json"
	"fmt"
	"testing"
)

type dataset struct {
	Active  bool   `json:"active"`
	Country string `json:"country"`
	Name    string `json:"name"`
	Url     string `json:"url"`
}

func TestRoutesWhitelist(t *testing.T) {
	var datasets []dataset
	var routesWhitelist map[string]map[string][]string

	if err := json.Unmarshal(routesWhitelistFile, &routesWhitelist); err != nil {
		t.Fatal(err)
	}

	for datasetName, allowedSegmentTypes := range routesWhitelist["types"] {
		for _, segmentType := range allowedSegmentTypes {
			if _, ok := whitelistTypeMapping[segmentType]; !ok {
				t.Error(fmt.Errorf("%s contains an unsupported segment type: %s", datasetName, segmentType))
			}
		}
	}

	if err := json.Unmarshal(datasetsFile, &datasets); err != nil {
		t.Fatal(err)
	}

	for _, ds := range datasets {
		if _, ok := routesWhitelist[ds.Name]; !ok {
			t.Error(fmt.Errorf("%s has no whitelist configured", ds.Name))
		}
	}

	for _, datasetName := range []string{"ssim", "directferries"} {
		if _, ok := routesWhitelist[datasetName]; !ok {
			t.Error(fmt.Errorf("%s has no whitelist configured", datasetName))
		}
	}
}
