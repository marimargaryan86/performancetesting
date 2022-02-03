package legacy

type Repository struct {
	routes        []*Route
	routeSegments []*RouteSegment
	stops         []*Stop
	transfers     []*Transfer
	trips         []*Trip
	tripSegments  []*TripSegment
}

func NewRepository(
	routes []*Route,
	routeSegments []*RouteSegment,
	stops []*Stop,
	transfers []*Transfer,
	trips []*Trip,
	tripSegments []*TripSegment,
) *Repository {
	return &Repository{
		routes:        routes,
		routeSegments: routeSegments,
		stops:         stops,
		transfers:     transfers,
		trips:         trips,
		tripSegments:  tripSegments,
	}
}

func (r *Repository) RouteByRouteSegment(s *RouteSegment) *Route {
	return r.RouteBySequence(s.RouteSequence)
}

func (r *Repository) RouteBySequence(s uint64) *Route {
	return r.routes[s]
}

func (r *Repository) RouteSegmentBySequence(s uint64) *RouteSegment {
	return r.routeSegments[s]
}

func (r *Repository) StopBySequence(s uint64) *Stop {
	return r.stops[s]
}

func (r *Repository) TransferBySequence(s uint64) *Transfer {
	return r.transfers[s]
}

func (r *Repository) TripBySequence(s uint64) *Trip {
	return r.trips[s]
}

func (r *Repository) TripSegmentBySequence(s uint64) *TripSegment {
	return r.tripSegments[s]
}
