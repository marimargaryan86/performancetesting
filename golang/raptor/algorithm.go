package raptor

import (
	"git.snowfall.se/junction/junction/golang/legacy"
	models "git.snowfall.se/junction/junction/golang/protobuf/snowfall/common/v1alpha"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/junction/planner/v1alpha"
	"github.com/uber/h3-go"
	"math"
	"runtime"
	"sort"
	"strconv"
	"sync"
	"time"
)

const airPrefixSeconds = 5400
const airSuffixSeconds = 3600
const railPrefixSeconds = 1800
const railSuffixSeconds = 900

type raptor struct {
	best          *sync.Map
	connections   map[uint64]map[uint8]interface{}
	data          *legacy.Repository
	destinations  []*planner.Stop
	lastDeparture uint32
	tripCutOff    uint32
	marked        []uint64
	round         uint8
	rounds        []*sync.Map
	trips         *sync.Map
	kindList      []models.Schedule_Type
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

func (r *raptor) initRound() {
	r.round++
	r.rounds = append(r.rounds, &sync.Map{})
}

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

func (r *raptor) markStops() bool {
	r.marked = make([]uint64, 0)

	r.rounds[r.round].Range(func(key, value interface{}) bool {
		r.marked = append(r.marked, key.(uint64))

		return true
	})

	return len(r.marked) != 0
}

func (r *raptor) queue() []uint64 {
	qMap := make(map[uint64]uint64, len(r.marked))

	for _, stopSequence := range r.marked {
		stop := r.data.StopBySequence(stopSequence)
		arrival, _ := r.rounds[r.round-1].Load(stop.Sequence)

		for _, routeSegmentSequence := range stop.RouteStops {
			routeSegment := r.data.RouteStopBySequence(routeSegmentSequence)
			route := r.data.RouteBySequence(routeSegment.Route)

			if int(routeSegment.Order+1) == len(route.RouteStops) {
				continue
			}

			trip := r.data.ScheduleBySequence(route.Schedules[len(route.Schedules)-1])
			tripSegment := r.data.ScheduleStopBySequence(trip.ScheduleStops[routeSegment.Order])

			if tripSegment.DepartureAt < arrival.(uint32) {
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
		tripSegment := result.stop
		arrival := result.arrival
		current := result.current
		boarding := result.boarding

		if r.isBetter(tripSegment.Stop, arrival) {
			r.rounds[r.round].Store(tripSegment.Stop, arrival)
			r.best.Store(tripSegment.Stop, arrival)

			if _, ok := r.connections[tripSegment.Stop]; !ok {
				r.connections[tripSegment.Stop] = make(map[uint8]interface{})
			}

			r.connections[tripSegment.Stop][r.round] = connection{
				schedule: current,
				from:     boarding,
				to:       tripSegment.Order,
			}
		}
	}
}

func (r *raptor) routeWorker(wg *sync.WaitGroup, jobs chan uint64, results chan workerResult) {
	defer wg.Done()

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

				if tripSegment.ArrivalAt == 0 {
					current = nil
				} else {
					arrival = tripSegment.ArrivalAt

					// adds additional transfer time based on origin type
					switch r.data.ScheduleBySequence(tripSegment.Schedule).Type {
					case models.Schedule_TYPE_AIR:
						arrival += airSuffixSeconds
					case models.Schedule_TYPE_RAIL:
						arrival += railSuffixSeconds
					}

					if r.isBetter(tripSegment.Stop, arrival) {
						results <- workerResult{
							stop:     tripSegment,
							arrival:  arrival,
							current:  current,
							boarding: boarding,
						}
					}
				}
			}

			previousArrival, ok := r.rounds[r.round-1].Load(routeSegment.Stop)

			if ok && (current == nil || previousArrival.(uint32) < arrival) {
				current = nil
				index, ok := r.trips.Load(qRoute.Sequence)

				if !ok {
					index = sort.Search(len(qRoute.Schedules)-1, func(i int) bool {
						trip := r.data.ScheduleBySequence(qRoute.Schedules[i])
						tripSegment := r.data.ScheduleStopBySequence(trip.ScheduleStops[routeSegment.Order])
						return tripSegment.DepartureAt > r.earliestPossibleDeparture(tripSegment, previousArrival.(uint32))
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

					if r.round == 1 && departure > r.lastDeparture || departure > r.tripCutOff {
						continue
					}

					if departure < r.earliestPossibleDeparture(tripSegment, previousArrival.(uint32)) {
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
