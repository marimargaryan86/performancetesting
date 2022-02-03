package legacy

import "github.com/golang/geo/s2"

const earthRadius = 6371.01

func Distance(p1 s2.LatLng, p2 s2.LatLng) float64 {
	a := p1.Distance(p2)

	return float64(a) * earthRadius * 1000
}
