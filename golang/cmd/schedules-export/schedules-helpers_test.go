package main

import (
	"testing"

	v1alpha "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"
)

func TestGetGeoIdentifier(t *testing.T) {
	// Minimal test until I can find an independent source of
	// lat/lon -> H3 values
	// Use http://wolf-h3-viewer.glitch.me/ to get test values
	h3 := getGeoIdentifier(&v1alpha.Coordinates{
		Latitude:  0.0,
		Longitude: 0.0,
	})
	if h3 != 0x89754e64993ffff {
		t.Errorf("Wrong geoIdentifier")
	}

	h3 = getGeoIdentifier(&v1alpha.Coordinates{
		Latitude:  51.38201,
		Longitude: -1.59814, // 9 Spaines, SN8 3LT
	})
	// hex := fmt.Sprintf("%x", h3)
	// fmt.Println(hex)
	if h3 != 0x891959d0583ffff {
		t.Errorf("Wrong geoIdentifier")
	}

}

func TestMaxU32(t *testing.T) {
	testCases := []struct {
		a, b, result uint32
	}{
		{1, 2, 2},
		{11, 11, 11},
		{0, 0, 0},
		{2, 0, 2},
		{0, 2, 2},
	}
	for _, tc := range testCases {
		if maxU32(tc.a, tc.b) != tc.result {
			t.Errorf("maxU32 (%v, %v) expcted %v got %v\n", tc.a, tc.b, tc.result, maxU32(tc.a, tc.b))
		}
	}
}
