package main

import (
	"encoding/json"
	"fmt"
	"testing"
	"time"
)

func TestAirlines(t *testing.T) {
	var airlinesList []string

	if err := json.Unmarshal(airlinesFile, &airlinesList); err != nil {
		t.Fatal(err)
	}

	for _, airline := range airlinesList {
		if len(airline) != 2 {
			t.Error(fmt.Errorf("%s is not two characters long", airline))
		}
	}
}

func TestAirports(t *testing.T) {
	var airports []Airport

	if err := json.Unmarshal(airportsFile, &airports); err != nil {
		t.Fatal(err)
	}

	for _, airport := range airports {
		if airport.Latitude < -90 || airport.Latitude > 90 {
			t.Error(fmt.Errorf("%s: %f is a valid latitude", airport.Name, airport.Latitude))
		}

		if airport.Longitude < -180 || airport.Longitude > 180 {
			t.Error(fmt.Errorf("%s: %f is not a valid longitude", airport.Name, airport.Longitude))
		}

		if len(airport.IataCode) != 3 {
			t.Error(fmt.Errorf("%s: %s is not three characters long", airport.Name, airport.IataCode))
		}

		if _, err := time.LoadLocation(airport.TimeZone); err != nil {
			t.Error(fmt.Errorf("%s: %s is not a valid time zone: %w", airport.Name, airport.TimeZone, err))
		}
	}
}
