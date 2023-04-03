package raptor

import (
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/go/service/planner/v1alpha"
	"github.com/google/uuid"
	"strings"
	"time"
)

type TripSet struct {
	Trips []*Trip
}

type Trip struct {
	Id       uuid.UUID
	Segments []*Segment
}

type Segment struct {
	Id         uuid.UUID
	ScheduleId uuid.UUID
	Depart     time.Time
	Arrive     time.Time
	Stops      []*Stop
}

type Stop struct {
	Id       string
	Sequence int64
}

var namespace uuid.UUID

func init() {
	namespace = uuid.NewSHA1(uuid.MustParse("271aa9c1-70c9-46ca-88a5-597ba261c14b"), []byte("snowfall"))
}

func (p *Planner) toJourneySet(destination *planner.Stop, connections map[uint64]map[uint8]interface{}) (*TripSet, error) {
	trips := make([]*Trip, 0)

	for k := range connections[destination.Sequence] {
		dest := destination
		segments := make([]*Segment, 0)

		for k > 0 {
			conn := connections[dest.Sequence][k]
			switch v := conn.(type) {
			case connection:
				from := p.data.ScheduleStopBySequence(v.schedule.ScheduleStops[v.from])
				to := p.data.ScheduleStopBySequence(v.schedule.ScheduleStops[v.to])
				stops := make([]*Stop, 0)

				for _, s := range v.schedule.ScheduleStops[v.from : v.to+1] {
					sScheduleStop := p.data.ScheduleStopBySequence(s)
					stops = append(stops, &Stop{
						Id:       sScheduleStop.Id,
						Sequence: int64(sScheduleStop.Sequence),
					})
				}

				org := p.data.StopBySequence(from.Stop)
				depart := from.DepartureAt
				arrive := to.ArrivalAt
				segmentIdParts := make([]string, 0, len(segments))

				for _, s := range stops {
					segmentIdParts = append(segmentIdParts, s.Id)
				}

				segments = append(segments, &Segment{
					Id:         uuid.NewSHA1(namespace, []byte(strings.Join(segmentIdParts, "\x00"))),
					ScheduleId: uuid.MustParse(v.schedule.Id),
					Stops:      stops,
					Depart:     time.Unix(int64(depart), 0),
					Arrive:     time.Unix(int64(arrive), 0),
				})

				dest = org
				k--
			case transfer:
				dest = v.from
			}
		}

		for i, j := 0, len(segments)-1; i < j; i, j = i+1, j-1 {
			segments[i], segments[j] = segments[j], segments[i]
		}

		tripIdParts := make([]string, 0, len(segments))

		for _, s := range segments {
			tripIdParts = append(tripIdParts, s.Id.String())
		}

		trips = append(trips, &Trip{
			Id:       uuid.NewSHA1(namespace, []byte(strings.Join(tripIdParts, "_"))),
			Segments: segments,
		})
	}

	return &TripSet{Trips: trips}, nil
}
