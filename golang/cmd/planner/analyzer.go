package main

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/legacy"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/go/service/planner/v1"
	models "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/go/v1"
	"git.snowfall.se/junction/junction/golang/raptor"
	"git.snowfall.se/junction/junction/golang/stdlib/sliceutil"
	"time"
)

type analyzer struct {
	analyzed        map[string]struct{}
	departureTimes  map[string][]time.Time
	departureAfter  time.Time
	departureBefore time.Time
	repository      *legacy.Repository
	tripCutoff      time.Time
}

func makeSegmentKey(o *planner.ScheduleStop, d *planner.ScheduleStop, t models.Schedule_Type) string {
	return fmt.Sprintf("%d_%d_%s", o.Stop, d.Stop, t)
}

func (a *analyzer) analyze(s *raptor.Segment) {
	origin := a.repository.ScheduleStopBySequence(s.Stops[0].Sequence)
	destination := a.repository.ScheduleStopBySequence(s.Stops[len(s.Stops)-1].Sequence)
	segmentKey := makeSegmentKey(origin, destination, s.Type)
	route := a.repository.RouteBySequence(s.RouteIndex)
	cacheKey := fmt.Sprintf("%d_%s", route.Sequence, segmentKey)

	if _, ok := a.analyzed[cacheKey]; ok {
		return
	}

	a.analyzed[cacheKey] = struct{}{}
	schedules := route.GetSchedules()
	idx := sliceutil.Index(schedules, s.ScheduleIndex)
	numDepartures := uint32(1)
	departureTimes := []time.Time{
		time.Unix(int64(a.repository.ScheduleStopBySequence(
			a.repository.ScheduleBySequence(s.ScheduleIndex).ScheduleStops[origin.Order],
		).DepartureAt), 0),
	}

	for i := idx - 1; i >= 0; i-- {
		deparatureAt := time.Unix(int64(a.repository.ScheduleStopBySequence(
			a.repository.ScheduleBySequence(schedules[i]).ScheduleStops[origin.Order],
		).DepartureAt), 0)

		if deparatureAt.After(a.tripCutoff) {
			continue
		}

		if deparatureAt.Before(a.departureAfter) {
			break
		}

		departureTimes = append(departureTimes, deparatureAt)

		if deparatureAt.Before(a.departureBefore) {
			numDepartures++
		}
	}

	for i := idx + 1; i < len(schedules); i++ {
		deparatureAt := time.Unix(int64(a.repository.ScheduleStopBySequence(
			a.repository.ScheduleBySequence(schedules[i]).ScheduleStops[origin.Order],
		).DepartureAt), 0)

		if deparatureAt.After(a.tripCutoff) {
			break
		}

		if deparatureAt.Before(a.departureAfter) {
			continue
		}

		departureTimes = append(departureTimes, deparatureAt)

		if deparatureAt.Before(a.departureBefore) {
			numDepartures++
		}
	}

	if _, ok := a.departureTimes[segmentKey]; !ok {
		a.departureTimes[segmentKey] = make([]time.Time, 0)
	}

	a.departureTimes[segmentKey] = append(a.departureTimes[segmentKey], departureTimes...)
}
