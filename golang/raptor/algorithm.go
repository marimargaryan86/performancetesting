package raptor

import (
	"git.snowfall.se/junction/junction/golang/legacy"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/service/planner/v1alpha"
	models "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"
	"github.com/uber/h3-go"
	"math"
	"runtime"
	"sort"
	"strconv"
	"sync"
	"time"
)

var transferTimeTable = map[transferTime]uint32{
	{models.Schedule_TYPE_AIR, true, models.Schedule_TYPE_AIR, true}:     105,
	{models.Schedule_TYPE_AIR, true, models.Schedule_TYPE_AIR, false}:    105,
	{models.Schedule_TYPE_AIR, true, models.Schedule_TYPE_RAIL, true}:    180,
	{models.Schedule_TYPE_AIR, true, models.Schedule_TYPE_RAIL, false}:   180,
	{models.Schedule_TYPE_AIR, false, models.Schedule_TYPE_AIR, true}:    105,
	{models.Schedule_TYPE_AIR, false, models.Schedule_TYPE_AIR, false}:   105,
	{models.Schedule_TYPE_AIR, false, models.Schedule_TYPE_RAIL, true}:   180,
	{models.Schedule_TYPE_AIR, false, models.Schedule_TYPE_RAIL, false}:  180,
	{models.Schedule_TYPE_RAIL, true, models.Schedule_TYPE_AIR, true}:    180,
	{models.Schedule_TYPE_RAIL, true, models.Schedule_TYPE_AIR, false}:   180,
	{models.Schedule_TYPE_RAIL, true, models.Schedule_TYPE_RAIL, true}:   45,
	{models.Schedule_TYPE_RAIL, true, models.Schedule_TYPE_RAIL, false}:  45,
	{models.Schedule_TYPE_RAIL, false, models.Schedule_TYPE_AIR, true}:   180,
	{models.Schedule_TYPE_RAIL, false, models.Schedule_TYPE_AIR, false}:  180,
	{models.Schedule_TYPE_RAIL, false, models.Schedule_TYPE_RAIL, true}:  45,
	{models.Schedule_TYPE_RAIL, false, models.Schedule_TYPE_RAIL, false}: 45,
}

type transferTime struct {
	prevScheduleType  models.Schedule_Type
	prevInternational bool
	nextScheduleType  models.Schedule_Type
	nextInternational bool
}

type raptor struct {
	best          *sync.Map                        // a map of route stops to earliest possible arrival to them, key type is Stop.Sequence, value type is unix timestamp
	connections   map[uint64]map[uint8]interface{} // a map of ScheduleStops to a map of round number to type connection
	data          *legacy.Repository               // helper functions to get objects from different ids
	destinations  []*planner.Stop                  // list of destination stops
	lastDeparture uint32                           // the last time considered to depart from the origin
	tripCutOff    uint32                           // the last time considered to arrive at the destination
	marked        []uint64                         // a list of stops we can start from in the current round
	round         uint8                            // an index of the round, starts at 0
	rounds        []*sync.Map                      // a map of round number to a map of Stop.Sequence to unix timestamps (basically a round number to that rounds `best`)
	trips         *sync.Map                        // a map of route.Sequence to index of route.Schedules
	kindList      []models.Schedule_Type           // list of schedule types to search for
	stopsMap      map[h3.H3Index][]*planner.Stop
}

type connection struct {
	schedule *planner.Schedule
	from     uint32
	to       uint32
}

type transfer struct {
	from      *planner.Stop
	to        *planner.Stop
	departure uint32
	arrival   uint32
	kind      models.Schedule_Type
}

type workerResult struct {
	stop     *planner.ScheduleStop
	arrival  uint32
	current  *planner.Schedule
	boarding uint32
}

// initializes the raptor object
func newRaptor(
	data *legacy.Repository,
	origins []*planner.Stop,
	destinations []*planner.Stop,
	departureAt time.Time,
	kindList []models.Schedule_Type,
	stopsMap map[h3.H3Index][]*planner.Stop,
) *raptor {
	y, m, d := departureAt.AddDate(0, 0, 1).Date()
	best := &sync.Map{}
	rounds := []*sync.Map{0: {}}
	marked := make([]uint64, 0, len(origins))
	departureAtTs := uint32(departureAt.Unix())

	for _, origin := range origins {
		best.Store(origin.Sequence, departureAtTs)
		rounds[0].Store(origin.Sequence, departureAtTs)
		marked = append(marked, origin.Sequence)
	}

	return &raptor{
		best:          best,
		connections:   map[uint64]map[uint8]interface{}{},
		data:          data,
		destinations:  destinations,
		lastDeparture: uint32(time.Date(y, m, d, 4, 0, 0, 0, departureAt.Location()).Unix()),
		tripCutOff:    uint32(departureAt.Add(48 * time.Hour).Unix()),
		marked:        marked,
		round:         0,
		rounds:        rounds,
		trips:         &sync.Map{},
		kindList:      kindList,
		stopsMap:      stopsMap,
	}
}

// increases the r.round number by one and initializes the r.rounds to an empty map
func (r *raptor) initRound() {
	r.round++
	r.rounds = append(r.rounds, &sync.Map{})
}

// check if this is the earliest arrival to the stop so far
func (r *raptor) isBetter(stopSequence uint64, arrival uint32) bool {
	best := uint32(math.MaxUint32)

	if v, ok := r.best.Load(stopSequence); ok {
		best = v.(uint32)
	}

	for _, destination := range r.destinations {
		if v, ok := r.best.Load(destination.Sequence); ok && v.(uint32) < best {
			best = v.(uint32)
		}
	}

	return arrival < best
}

// adds stops reached in the last round to r.marked
// returns true if r.marked is not empty
func (r *raptor) markStops() bool {
	r.marked = make([]uint64, 0)

	r.rounds[r.round].Range(func(key, value interface{}) bool {
		r.marked = append(r.marked, key.(uint64))

		return true
	})

	return len(r.marked) != 0
}

// adds all earliest schedule segments from route segments that can be reached
// from stops in the r.marked list
func (r *raptor) queue() []uint64 {
	qMap := make(map[uint64]uint64, len(r.marked))

	for _, stopSequence := range r.marked {
		stop := r.data.StopBySequence(stopSequence)
		arrival, _ := r.rounds[r.round-1].Load(stop.Sequence)

		for _, routeStopSequence := range stop.RouteStops {
			routeStop := r.data.RouteStopBySequence(routeStopSequence)
			route := r.data.RouteBySequence(routeStop.Route)

			if int(routeStop.Order+1) == len(route.RouteStops) {
				continue
			}

			trip := r.data.ScheduleBySequence(route.Schedules[len(route.Schedules)-1])
			tripScheduleStop := r.data.ScheduleStopBySequence(trip.ScheduleStops[routeStop.Order])

			if tripScheduleStop.DepartureAt < arrival.(uint32) {
				continue
			}

			if val, ok := qMap[route.Sequence]; (ok && routeStop.Sequence < val) || !ok {
				qMap[route.Sequence] = routeStop.Sequence
			}
		}
	}

	q := make([]uint64, 0, len(qMap))

	for _, v := range qMap {
		q = append(q, v)
	}

	return q
}

// initializes routeWorker functions that return the earliest possible schedule
// and updates the r.connections map with the result
func (r *raptor) scanRoutes() {
	wg := &sync.WaitGroup{}
	qItems := r.queue()
	results := make(chan workerResult, len(qItems))
	jobs := make(chan uint64, len(qItems))

	for w := 1; w <= runtime.NumCPU(); w++ {
		wg.Add(1)
		go r.routeWorker(wg, jobs, results)
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	for _, qItem := range qItems {
		jobs <- qItem
	}

	close(jobs)

	for result := range results {
		tripScheduleStop := result.stop
		arrival := result.arrival
		current := result.current
		boarding := result.boarding

		if r.isBetter(tripScheduleStop.Stop, arrival) {
			r.rounds[r.round].Store(tripScheduleStop.Stop, arrival)
			r.best.Store(tripScheduleStop.Stop, arrival)

			if _, ok := r.connections[tripScheduleStop.Stop]; !ok {
				r.connections[tripScheduleStop.Stop] = make(map[uint8]interface{})
			}

			r.connections[tripScheduleStop.Stop][r.round] = connection{
				schedule: current,
				from:     boarding,
				to:       tripScheduleStop.Order,
			}
		}
	}
}

// finds the earliest possible transfer (schedule) from routes that satisfy the (originRouteStop, destinationRouteStop, departure) triplet
func (r *raptor) routeWorker(wg *sync.WaitGroup, jobs chan uint64, results chan workerResult) {
	defer wg.Done()

	for qItem := range jobs {
		qRouteStop := r.data.RouteStopBySequence(qItem)
		qRoute := r.data.RouteByRouteStop(qRouteStop)

		var current *planner.Schedule
		var boarding uint32

		for _, p := range qRoute.RouteStops[qRouteStop.Order:] {
			routeStop := r.data.RouteStopBySequence(p)

			var arrival uint32

			if current != nil {
				tripScheduleStop := r.data.ScheduleStopBySequence(current.ScheduleStops[routeStop.Order])

				if tripScheduleStop.ArrivalAt == 0 {
					current = nil
				} else {
					arrival = tripScheduleStop.ArrivalAt

					// adds additional transfer time based on origin type
					arrival = r.earliestPossibleDeparture(tripScheduleStop, arrival)

					if r.isBetter(tripScheduleStop.Stop, arrival) {
						results <- workerResult{
							stop:     tripScheduleStop,
							arrival:  arrival,
							current:  current,
							boarding: boarding,
						}
					}
				}
			}

			previousArrival, ok := r.rounds[r.round-1].Load(routeStop.Stop)

			if ok && (current == nil || previousArrival.(uint32) < arrival) {
				current = nil
				index, ok := r.trips.Load(qRoute.Sequence)

				if !ok {
					index = sort.Search(len(qRoute.Schedules)-1, func(i int) bool {
						trip := r.data.ScheduleBySequence(qRoute.Schedules[i])
						tripScheduleStop := r.data.ScheduleStopBySequence(trip.ScheduleStops[routeStop.Order])
						return tripScheduleStop.DepartureAt > r.earliestPossibleDeparture(tripScheduleStop, previousArrival.(uint32))
					})
					r.trips.Store(qRoute.Sequence, index)
				}

				for i := index.(int); i >= 0; i-- {
					trip := r.data.ScheduleBySequence(qRoute.Schedules[i])
					found := false

					for _, tid := range r.kindList {
						if tid == trip.Type {
							found = true
							break
						}
					}

					if !found {
						continue
					}

					tripScheduleStop := r.data.ScheduleStopBySequence(trip.ScheduleStops[routeStop.Order])
					departure := tripScheduleStop.DepartureAt

					if r.round == 1 && departure > r.lastDeparture || departure > r.tripCutOff {
						continue
					}

					if departure < r.earliestPossibleDeparture(tripScheduleStop, previousArrival.(uint32)) {
						break
					}

					current = trip
					boarding = tripScheduleStop.Order
					r.trips.Store(qRoute.Sequence, i)
				}
			}
		}
	}
}

// adds additional transfer time based on destination type
func (r *raptor) earliestPossibleDeparture(target *planner.ScheduleStop, previousArrival uint32) uint32 {
	if r.round == 1 {
		return previousArrival
	}
	nextSchedule := r.data.ScheduleBySequence(target.Schedule)
	nextRoute := r.data.RouteBySequence(nextSchedule.Route)
	prevTransfer := r.connections[target.Sequence][r.round-1]
	switch prevTransfer.(type) {
	case transfer:
		prevTransfer = r.connections[prevTransfer.(transfer).from.Sequence][r.round-1]
	}
	switch prevTransfer.(type) {
	case connection:
		prevRoute := r.data.RouteBySequence(prevTransfer.(connection).schedule.Route)
		previousArrival += transferTimeTable[transferTime{
			prevScheduleType:  prevTransfer.(connection).schedule.Type,
			prevInternational: prevRoute.IsInternational,
			nextScheduleType:  nextSchedule.Type,
			nextInternational: nextRoute.IsInternational,
		}]
	case transfer:
		panic("A transfer has been made from a transfer in the same round.")
	}

	return previousArrival
}

// extends r.marked with all stops a person can walk to from stops already in
// r.marked by finding stops in the neighbouring h3 hexes
// updates the r.connections with the newly calculated transfer time
func (r *raptor) scanTransfers() {
	for _, p := range r.marked {
		fromStop := r.data.StopBySequence(p)
		departure, _ := r.rounds[r.round].Load(fromStop.Sequence)
		idInt, _ := strconv.ParseUint(fromStop.Id, 10, 0)
		hex := h3.H3Index(idInt)
		neighbours := h3.KRing(hex, 2)

		for _, n := range neighbours {
			toStops, ok := r.stopsMap[n]

			if !ok {
				continue
			}

			for _, toStop := range toStops {
				arrival := departure.(uint32) + (60 * 10) + toStop.TransferTime

				if r.isBetter(toStop.Sequence, arrival) {
					r.rounds[r.round].Store(toStop.Sequence, arrival)
					r.best.Store(toStop.Sequence, arrival)

					if _, ok := r.connections[toStop.Sequence]; !ok {
						r.connections[toStop.Sequence] = make(map[uint8]interface{})
					}

					r.connections[toStop.Sequence][r.round] = transfer{
						from:      fromStop,
						to:        toStop,
						departure: departure.(uint32),
						arrival:   departure.(uint32) + (60 * 10),
						kind:      models.Schedule_TYPE_UNSPECIFIED,
					}
				}
			}
		}

		for _, t := range fromStop.Transfers {
			trans := r.data.TransferBySequence(t)
			toStop := r.data.StopBySequence(trans.ToStop)
			arrival := departure.(uint32) + trans.TransferTime + toStop.TransferTime

			if r.isBetter(toStop.Sequence, arrival) {
				r.rounds[r.round].Store(toStop.Sequence, arrival)
				r.best.Store(toStop.Sequence, arrival)

				if _, ok := r.connections[toStop.Sequence]; !ok {
					r.connections[toStop.Sequence] = make(map[uint8]interface{})
				}

				r.connections[toStop.Sequence][r.round] = transfer{
					from:      fromStop,
					to:        toStop,
					departure: departure.(uint32),
					arrival:   departure.(uint32) + trans.TransferTime,
					kind:      trans.Type,
				}
			}
		}
	}
}

// run the raptor algorithm (the overview of the algorithm)
func (r *raptor) run() map[uint64]map[uint8]interface{} {
	r.scanTransfers()
	r.markStops()

	for {
		r.initRound()
		r.scanRoutes()

		if !r.markStops() {
			break
		}

		r.scanTransfers()
		r.markStops()
	}

	return r.connections
}
