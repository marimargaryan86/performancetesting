package legacy

import (
	"errors"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/junction/planner/v1alpha"
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
	for sequence, route := range routes {
		if uint64(sequence) != route.Sequence {
			return &Repository{}, errors.New("validation error: route: invalid sequence")
		}

		for _, schedule := range route.Schedules {
			if uint64(len(schedules)) <= schedule {
				return &Repository{}, errors.New("validation error: route: schedule out of range")
			}
		}

		for _, routeStop := range route.RouteStops {
			if uint64(len(routeStops)) <= routeStop {
				return &Repository{}, errors.New("validation error: route: route stop out of range")
			}
		}
	}

	for sequence, routeStop := range routeStops {
		if uint64(sequence) != routeStop.Sequence {
			return &Repository{}, errors.New("validation error: route stop: invalid sequence")
		}

		if uint64(len(routes)) <= routeStop.Route {
			return &Repository{}, errors.New("validation error: route stop: route out of range")
		}

		if uint64(len(stops)) <= routeStop.Stop {
			return &Repository{}, errors.New("validation error: route stop: stop out of range")
		}
	}

	for sequence, stop := range stops {
		if uint64(sequence) != stop.Sequence {
			return &Repository{}, errors.New("validation error: stop: invalid sequence")
		}

		for _, routeStop := range stop.RouteStops {
			if uint64(len(routeStops)) <= routeStop {
				return &Repository{}, errors.New("validation error: stop: route stop out of range")
			}
		}

		for _, scheduleStop := range stop.ScheduleStops {
			if uint64(len(scheduleStops)) <= scheduleStop {
				return &Repository{}, errors.New("validation error: stop: schedule stop out of range")
			}
		}

		for _, transfer := range stop.Transfers {
			if uint64(len(transfers)) <= transfer {
				return &Repository{}, errors.New("validation error: stop: transfer out of range")
			}
		}
	}

	for sequence, transfer := range transfers {
		if uint64(sequence) != transfer.Sequence {
			return &Repository{}, errors.New("validation error: transfer: invalid sequence")
		}

		if uint64(len(stops)) <= transfer.ToStop {
			return &Repository{}, errors.New("validation error: transfer: to stop out of range")
		}

		if uint64(len(stops)) <= transfer.FromStop {
			return &Repository{}, errors.New("validation error: transfer: from stop out of range")
		}
	}

	for sequence, schedule := range schedules {
		if uint64(sequence) != schedule.Sequence {
			return &Repository{}, errors.New("validation error: schedule: invalid sequence")
		}

		if uint64(len(routes)) <= schedule.Route {
			return &Repository{}, errors.New("validation error: schedule: route out of range")
		}

		for _, scheduleStop := range schedule.ScheduleStops {
			if uint64(len(scheduleStops)) <= scheduleStop {
				return &Repository{}, errors.New("validation error: schedule: schedule stop out of range")
			}
		}
	}

	for sequence, scheduleStop := range scheduleStops {
		if uint64(sequence) != scheduleStop.Sequence {
			return &Repository{}, errors.New("validation error: schedule stop: invalid sequence")
		}

		if uint64(len(schedules)) <= scheduleStop.Schedule {
			return &Repository{}, errors.New("validation error: schedule stop: schedule out of range")
		}

		if uint64(len(stops)) <= scheduleStop.Stop {
			return &Repository{}, errors.New("validation error: schedule stop: stop out of range")
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
