package main

import (
	"fmt"
	"testing"

	v1alpha "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"
)

func TestGetGeoIdentifier(t *testing.T) {
	// Minimal test until I can find an independent source of
	// lat/lon -> H3 values
	// Use http://wolf-h3-viewer.glitch.me/ to get test values
	h3 := getGeoIdentifier(&v1alpha.LatLng{
		Latitude:  0.0,
		Longitude: 0.0,
	})
	if h3 != 0x89754e64993ffff {
		t.Errorf("Wrong geoIdentifier")
	}

	h3 = getGeoIdentifier(&v1alpha.LatLng{
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
		a, b, want uint32
	}{
		{1, 2, 2},
		{11, 11, 11},
		{0, 0, 0},
		{2, 0, 2},
		{0, 2, 2},
	}
	for _, tc := range testCases {
		t.Run(fmt.Sprintf("max(%d, %d)", tc.a, tc.b), func(t *testing.T) {

		})
		if got := maxU32(tc.a, tc.b); got != tc.want {
			t.Errorf("got %d; want %d", got, tc.want)
		}
	}
}
