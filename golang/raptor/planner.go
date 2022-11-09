package raptor

import (
	"git.snowfall.se/junction/junction/golang/legacy"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/service/planner/v1alpha"
	models "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"
	"github.com/google/uuid"
	"github.com/uber/h3-go"
	"runtime"
	"sort"
	"time"

	"go.uber.org/zap"
)

type Planner struct {
	data     *legacy.Repository
	logger   *zap.SugaredLogger
	stopsMap map[h3.H3Index][]*planner.Stop
}

func NewPlanner(
	data *legacy.Repository,
	stopsMap map[h3.H3Index][]*planner.Stop,
	logger *zap.SugaredLogger,
) *Planner {
	return &Planner{
		data:     data,
		logger:   logger,
		stopsMap: stopsMap,
	}
}

func (p *Planner) Search(froms []*planner.Stop, tos []*planner.Stop, departureAt time.Time, kindList []models.Schedule_Type, maxConnections int) ([]*Trip, error) {
	if len(kindList) == 0 {
		kindList = []models.Schedule_Type{
			models.Schedule_TYPE_UNSPECIFIED,
			models.Schedule_TYPE_AIR,
			models.Schedule_TYPE_RAIL,
		}
	}

	seen := make(map[uuid.UUID]struct{})
	trips := make([]*Trip, 0)
	iterations := 0
	start := time.Now()
	sTime := departureAt
	eTime := sTime.AddDate(0, 0, 1)
	eTime = time.Date(eTime.Year(), eTime.Month(), eTime.Day(), 4, 0, 0, 0, eTime.Location())

	for sTime.Before(eTime) {
		iterations++

		r := newRaptor(p.data, froms, tos, sTime, kindList, p.stopsMap, maxConnections)
		results := r.run()
		min := eTime
		found := false

		for _, to := range tos {
			result, err := p.toJourneySet(to, results)

			if err != nil {
				return trips, err
			}

			if len(result.Trips) == 0 {
				continue
			}

			found = true

			for _, s := range result.Trips {
				if s.Segments[0].Depart.Before(min) {
					min = s.Segments[0].Depart.In(sTime.Location())
				}

				if _, ok := seen[s.Id]; ok {
					continue
				}

				seen[s.Id] = struct{}{}

				trips = append(trips, s)
			}
		}

		if !found {
			break
		}

		sTime = min.Add(time.Minute)
	}

	sort.SliceStable(trips, func(i, j int) bool {
		one := trips[i].Segments
		two := trips[j].Segments

		if one[len(one)-1].Arrive == two[len(two)-1].Arrive {
			return one[0].Depart.Before(two[0].Depart)
		}

		return one[len(one)-1].Arrive.Before(two[len(two)-1].Arrive)
	})

	for i := 0; i < len(trips); {
		if i == len(trips)-1 {
			break
		}

		current := trips[i]
		next := trips[i+1]

		if next.Segments[len(next.Segments)-1].Arrive.After(current.Segments[len(current.Segments)-1].Arrive) || len(next.Segments) > len(current.Segments) {
			i++
		} else {
			copy(trips[i:], trips[i+1:]) // Shift a[i+1:] left one index.
			trips[len(trips)-1] = &Trip{}
			trips = trips[:len(trips)-1]
		}
	}

	fromIds := make([]string, 0, len(froms))
	toIds := make([]string, 0, len(tos))

	for _, from := range froms {
		fromIds = append(fromIds, from.Id)
	}

	for _, to := range tos {
		toIds = append(toIds, to.Id)
	}

	p.logger.Infow(
		"search performed",
		"origins", fromIds,
		"destinations", toIds,
		"departure", departureAt.Format(time.RFC3339),
		"iterations", iterations,
		"results", len(trips),
		"workers", runtime.NumCPU(),
		"exec", time.Since(start),
	)

	return trips, nil
}
