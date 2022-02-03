package raptor

import (
	"git.snowfall.se/junction/junction/golang/legacy"
	"math"
	"runtime"
	"sort"
	"sync"
	"time"
)

type raptor struct {
	best          *sync.Map
	connections   map[uint64]map[uint8]interface{}
	data          *legacy.Repository
	destinations  []*legacy.Stop
	lastDeparture uint32
	tripCutOff    uint32
	marked        []uint64
	round         uint8
	rounds        []*sync.Map
	trips         *sync.Map
	kindList      []legacy.Trip_Kind
}

type connection struct {
	trip *legacy.Trip
	from uint32
	to   uint32
}

type transfer struct {
	from      *legacy.Stop
	to        *legacy.Stop
	departure uint32
	arrival   uint32
	kind      legacy.Trip_Kind
}

type workerResult struct {
	segment  *legacy.TripSegment
	arrival  uint32
	current  *legacy.Trip
	boarding uint32
}

func newRaptor(
	data *legacy.Repository,
	origins []*legacy.Stop,
	destinations []*legacy.Stop,
	departureAt time.Time,
	kindList []legacy.Trip_Kind,
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

		for _, routeSegmentSequence := range stop.RouteSegments {
			routeSegment := r.data.RouteSegmentBySequence(routeSegmentSequence)
			route := r.data.RouteBySequence(routeSegment.RouteSequence)

			if int(routeSegment.Order+1) == len(route.RouteSegments) {
				continue
			}

			trip := r.data.TripBySequence(route.Trips[len(route.Trips)-1])
			tripSegment := r.data.TripSegmentBySequence(trip.TripSegments[routeSegment.Order])

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
		tripSegment := result.segment
		arrival := result.arrival
		current := result.current
		boarding := result.boarding

		if r.isBetter(tripSegment.StopSequence, arrival) {
			r.rounds[r.round].Store(tripSegment.StopSequence, arrival)
			r.best.Store(tripSegment.StopSequence, arrival)

			if _, ok := r.connections[tripSegment.StopSequence]; !ok {
				r.connections[tripSegment.StopSequence] = make(map[uint8]interface{})
			}

			r.connections[tripSegment.StopSequence][r.round] = connection{
				trip: current,
				from: boarding,
				to:   tripSegment.Order,
			}
		}
	}
}

func (r *raptor) routeWorker(wg *sync.WaitGroup, jobs chan uint64, results chan workerResult) {
	defer wg.Done()

	for qItem := range jobs {
		qRouteSegment := r.data.RouteSegmentBySequence(qItem)
		qRoute := r.data.RouteByRouteSegment(qRouteSegment)

		var current *legacy.Trip
		var boarding uint32

		for _, p := range qRoute.RouteSegments[qRouteSegment.Order:] {
			routeSegment := r.data.RouteSegmentBySequence(p)
			transferTime := r.data.StopBySequence(routeSegment.StopSequence).TransferTime

			var tripSegment *legacy.TripSegment

			if current != nil {
				tripSegment = r.data.TripSegmentBySequence(current.TripSegments[routeSegment.Order])
				arrival := tripSegment.ArrivalAt + transferTime

				if r.isBetter(tripSegment.StopSequence, arrival) {
					results <- workerResult{
						segment:  tripSegment,
						arrival:  arrival,
						current:  current,
						boarding: boarding,
					}
				}
			}

			previousArrival, ok := r.rounds[r.round-1].Load(routeSegment.StopSequence)

			if ok && (current == nil || previousArrival.(uint32) < tripSegment.ArrivalAt+transferTime) {
				current = nil
				index, ok := r.trips.Load(qRoute.Sequence)

				if !ok {
					index = sort.Search(len(qRoute.Trips)-1, func(i int) bool {
						trip := r.data.TripBySequence(qRoute.Trips[i])
						tripSegment := r.data.TripSegmentBySequence(trip.TripSegments[routeSegment.Order])
						return tripSegment.DepartureAt > previousArrival.(uint32)
					})
					r.trips.Store(qRoute.Sequence, index)
				}

				for i := index.(int); i >= 0; i-- {
					trip := r.data.TripBySequence(qRoute.Trips[i])
					found := false

					for _, tid := range r.kindList {
						if tid == trip.Kind {
							found = true
							break
						}
					}

					if !found {
						continue
					}

					tripSegment := r.data.TripSegmentBySequence(trip.TripSegments[routeSegment.Order])
					departure := tripSegment.DepartureAt

					if r.round == 1 && departure > r.lastDeparture || departure > r.tripCutOff {
						continue
					}

					if departure < previousArrival.(uint32) {
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

func (r *raptor) scanTransfers() {
	for _, p := range r.marked {
		fromStop := r.data.StopBySequence(p)
		departure, _ := r.rounds[r.round].Load(fromStop.Sequence)

		for _, t := range fromStop.Transfers {
			trans := r.data.TransferBySequence(t)
			toStop := r.data.StopBySequence(trans.ToStopSequence)
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
					kind:      trans.Kind,
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
