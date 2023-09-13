package legacy

import (
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/go/service/planner/v1"
	"github.com/uber/h3-go/v4"
	"strconv"
)

type Repository struct {
	routes        []*planner.Route
	routeStops    []*planner.RouteStop
	stops         []*planner.Stop
	transfers     []*planner.Transfer
	schedules     []*planner.Schedule
	scheduleStops []*planner.ScheduleStop
}

func NewRepository(
	routes []*planner.Route,
	routeStops []*planner.RouteStop,
	stops []*planner.Stop,
	transfers []*planner.Transfer,
	schedules []*planner.Schedule,
	scheduleStops []*planner.ScheduleStop,
) (*Repository, error) {
	nullIsland := h3.LatLngToCell(h3.NewLatLng(0, 0), 9)

	for _, stop := range stops {
		intIndex, _ := strconv.Atoi(stop.Id)

		if h3.Cell(intIndex) == nullIsland {
			for _, seq := range stop.ScheduleStops {
				scheduleStops[seq].AlightingAllowed = false
				scheduleStops[seq].BoardingAllowed = false
			}

			break
		}
	}

	return &Repository{
		routes:        routes,
		routeStops:    routeStops,
		stops:         stops,
		transfers:     transfers,
		schedules:     schedules,
		scheduleStops: scheduleStops,
	}, nil
}

func (r *Repository) RouteByRouteStop(s *planner.RouteStop) *planner.Route {
	return r.RouteBySequence(s.Route)
}

func (r *Repository) RouteBySequence(s uint64) *planner.Route {
	return r.routes[s]
}

func (r *Repository) RouteStopBySequence(s uint64) *planner.RouteStop {
	return r.routeStops[s]
}

func (r *Repository) StopBySequence(s uint64) *planner.Stop {
	return r.stops[s]
}

func (r *Repository) TransferBySequence(s uint64) *planner.Transfer {
	return r.transfers[s]
}

func (r *Repository) ScheduleBySequence(s uint64) *planner.Schedule {
	return r.schedules[s]
}

func (r *Repository) ScheduleStopBySequence(s uint64) *planner.ScheduleStop {
	return r.scheduleStops[s]
}
