package raptor

import (
	"git.snowfall.se/junction/junction/golang/legacy"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/go/service/planner/v1"
	models "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/go/v1"
	"github.com/uber/h3-go/v4"
	"math"
	"sort"
	"sync"
	"time"
)

const airPrefixSeconds = 4500
const airSuffixSeconds = 2700
const railPrefixSeconds = 1800
const railSuffixSeconds = 900

type raptor struct {
	best           map[uint64]uint32                // a map of route stops to earliest possible arrival to them, key type is Stop.Sequence, value type is unix timestamp
	connections    map[uint64]map[uint8]interface{} // a map of ScheduleStops to a map of round number to type connection
	data           *legacy.Repository               // helper functions to get objects from different ids
	destinations   []*planner.Stop                  // list of destination stops
	lastDeparture  uint32                           // the last time considered to depart from the origin
	tripCutOff     uint32                           // the last time considered to arrive at the destination
	marked         []uint64                         // a list of stops we can start from in the current round
	round          uint8                            // an index of the round, starts at 0
	rounds         []map[uint64]uint32              // a map of round number to a map of Stop.Sequence to unix timestamps (basically a round number to that rounds `best`)
	trips          *sync.Map                        // a map of route.Sequence to index of route.Schedules
	kindList       []models.Schedule_Type           // list of schedule types to search for
	stopsMap       map[h3.Cell][]*planner.Stop
	maxConnections int
	workerCount    int
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
	stopsMap map[h3.Cell][]*planner.Stop,
	maxConnections int,
	workerCount int,
) *raptor {
	y, m, d := departureAt.AddDate(0, 0, 1).Date()
	best := make(map[uint64]uint32)
	rounds := []map[uint64]uint32{0: {}}
	marked := make([]uint64, 0, len(origins))
	departureAtTs := uint32(departureAt.Unix())

	for _, origin := range origins {
		best[origin.Sequence] = departureAtTs
		rounds[0][origin.Sequence] = departureAtTs
		marked = append(marked, origin.Sequence)
	}

	return &raptor{
		best:           best,
		connections:    map[uint64]map[uint8]interface{}{},
		data:           data,
		destinations:   destinations,
		lastDeparture:  uint32(time.Date(y, m, d, 4, 0, 0, 0, departureAt.Location()).Unix()),
		tripCutOff:     uint32(departureAt.Add(48 * time.Hour).Unix()),
		marked:         marked,
		round:          0,
		rounds:         rounds,
		trips:          &sync.Map{},
		kindList:       kindList,
		stopsMap:       stopsMap,
		maxConnections: maxConnections,
		workerCount:    workerCount,
	}
}

// increases the r.round number by one and initializes the r.rounds to an empty map
func (r *raptor) initRound() {
	r.round++
	r.rounds = append(r.rounds, map[uint64]uint32{})
}

func (r *raptor) bestTimeAtDestination() uint32 {
	best := uint32(math.MaxUint32)

	for _, destination := range r.destinations {
		if v, ok := r.best[destination.Sequence]; ok && v < best {
			best = v
		}
	}

	return best
}

// check if this is the earliest arrival to the stop so far
func (r *raptor) isBetter(stopSequence uint64, arrival uint32) bool {
	best := uint32(math.MaxUint32)

	if v, ok := r.best[stopSequence]; ok {
		best = v
	}

	destination := r.bestTimeAtDestination()

	if destination < best {
		best = destination
	}

	return arrival < best
}

// adds stops reached in the last round to r.marked
// returns true if r.marked is not empty
func (r *raptor) markStops() bool {
	r.marked = make([]uint64, 0, len(r.rounds[r.round]))

	for stopSequence := range r.rounds[r.round] {
		r.marked = append(r.marked, stopSequence)
	}

	return len(r.marked) != 0
}

// adds all earliest schedule segments from route segments that can be reached
// from stops in the r.marked list
func (r *raptor) queue() []uint64 {
	qMap := make(map[uint64]uint64, len(r.marked))

	for _, stopSequence := range r.marked {
		stop := r.data.StopBySequence(stopSequence)
		arrival, _ := r.rounds[r.round-1][stop.Sequence]

		for _, routeSegmentSequence := range stop.RouteStops {
			routeSegment := r.data.RouteStopBySequence(routeSegmentSequence)
			route := r.data.RouteBySequence(routeSegment.Route)

			if int(routeSegment.Order+1) == len(route.RouteStops) {
				continue
			}

			trip := r.data.ScheduleBySequence(route.Schedules[len(route.Schedules)-1])
			tripSegment := r.data.ScheduleStopBySequence(trip.ScheduleStops[routeSegment.Order])

			if tripSegment.DepartureAt < arrival {
				continue
			}

			if val, ok := qMap[route.Sequence]; (ok && routeSegment.Sequence < val) || !ok {
				qMap[route.Sequence] = routeSegment.Sequence
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

	for _, qItem := range qItems {
		jobs <- qItem
	}

	close(jobs)

	for w := 1; w <= r.workerCount; w++ {
		wg.Add(1)
		go r.routeWorker(wg, jobs, results)
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	candidates := make([]workerResult, 0)

	for result := range results {
		if r.isBetter(result.stop.Stop, result.arrival) {
			r.best[result.stop.Stop] = result.arrival
			candidates = append(candidates, result)
		}
	}

	bestAtDestination := r.bestTimeAtDestination()

	for _, candidate := range candidates {
		if candidate.arrival <= bestAtDestination && candidate.arrival == r.best[candidate.stop.Stop] {
			r.rounds[r.round][candidate.stop.Stop] = candidate.arrival

			if _, ok := r.connections[candidate.stop.Stop]; !ok {
				r.connections[candidate.stop.Stop] = make(map[uint8]interface{})
			}

			r.connections[candidate.stop.Stop][r.round] = connection{
				schedule: candidate.current,
				from:     candidate.boarding,
				to:       candidate.stop.Order,
			}
		}
	}
}

// finds the earliest possible transfer (schedule) from routes that satisfy the (originRouteStop, destinationRouteStop, departure) triplet
func (r *raptor) routeWorker(wg *sync.WaitGroup, jobs chan uint64, results chan workerResult) {
	defer wg.Done()

	lastRound := r.rounds[r.round-1]

	for qItem := range jobs {
		qRouteSegment := r.data.RouteStopBySequence(qItem)
		qRoute := r.data.RouteByRouteStop(qRouteSegment)

		var current *planner.Schedule
		var boarding uint32

		for _, p := range qRoute.RouteStops[qRouteSegment.Order:] {
			routeSegment := r.data.RouteStopBySequence(p)

			var arrival uint32

			if current != nil {
				tripSegment := r.data.ScheduleStopBySequence(current.ScheduleStops[routeSegment.Order])

				if !tripSegment.AlightingAllowed {
					continue
				}

				arrival = tripSegment.ArrivalAt

				// adds additional transfer time based on origin type
				switch r.data.ScheduleBySequence(tripSegment.Schedule).Type {
				case models.Schedule_TYPE_AIR:
					arrival += airSuffixSeconds
				case models.Schedule_TYPE_RAIL:
					arrival += railSuffixSeconds
				}

				results <- workerResult{
					stop:     tripSegment,
					arrival:  arrival,
					current:  current,
					boarding: boarding,
				}
			}

			previousArrival, ok := lastRound[routeSegment.Stop]

			if ok && (current == nil || previousArrival < arrival) {
				index, ok := r.trips.Load(qRoute.Sequence)

				if !ok {
					index = sort.Search(len(qRoute.Schedules)-1, func(i int) bool {
						trip := r.data.ScheduleBySequence(qRoute.Schedules[i])
						tripSegment := r.data.ScheduleStopBySequence(trip.ScheduleStops[routeSegment.Order])
						return tripSegment.DepartureAt > r.earliestPossibleDeparture(tripSegment, previousArrival)
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

					tripSegment := r.data.ScheduleStopBySequence(trip.ScheduleStops[routeSegment.Order])
					departure := tripSegment.DepartureAt

					if !tripSegment.BoardingAllowed || (r.round == 1 && departure > r.lastDeparture) || departure > r.tripCutOff {
						continue
					}

					if departure < r.earliestPossibleDeparture(tripSegment, previousArrival) {
						break
					}

					current = trip
					boarding = tripSegment.Order
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

	switch r.data.ScheduleBySequence(target.Schedule).Type {
	case models.Schedule_TYPE_AIR:
		previousArrival += airPrefixSeconds
	case models.Schedule_TYPE_RAIL:
		previousArrival += railPrefixSeconds
	}

	return previousArrival
}

// extends r.marked with all stops a person can walk to from stops already in
// r.marked by finding stops in the neighbouring h3 hexes
// updates the r.connections with the newly calculated transfer time
func (r *raptor) scanTransfers() {
	for _, p := range r.marked {
		fromStop := r.data.StopBySequence(p)
		departure, _ := r.rounds[r.round][fromStop.Sequence]

		for _, t := range fromStop.Transfers {
			trans := r.data.TransferBySequence(t)
			toStop := r.data.StopBySequence(trans.ToStop)
			arrival := departure + trans.TransferTime + toStop.TransferTime

			if r.isBetter(toStop.Sequence, arrival) {
				r.rounds[r.round][toStop.Sequence] = arrival
				r.best[toStop.Sequence] = arrival

				if _, ok := r.connections[toStop.Sequence]; !ok {
					r.connections[toStop.Sequence] = make(map[uint8]interface{})
				}

				r.connections[toStop.Sequence][r.round] = transfer{
					from:      fromStop,
					to:        toStop,
					departure: departure,
					arrival:   departure + trans.TransferTime,
					kind:      trans.Type,
				}
			}
		}
	}
}

func (r *raptor) hasReachedMaxConnections() bool {
	return r.maxConnections != -1 && int(r.round) == (r.maxConnections+1)
}

// run the raptor algorithm (the overview of the algorithm)
func (r *raptor) run() map[uint64]map[uint8]interface{} {
	r.scanTransfers()
	r.markStops()

	for {
		r.initRound()
		r.scanRoutes()

		if !r.markStops() || r.hasReachedMaxConnections() {
			break
		}

		r.scanTransfers()
		r.markStops()
	}

	return r.connections
}
