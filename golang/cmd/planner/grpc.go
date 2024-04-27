package main

import (
	"context"
	"errors"
	"git.snowfall.se/junction/junction/golang/legacy"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/go/service/planner/v1"
	models "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/go/v1"
	v1 "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/v1"
	v1Stdlib "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1"
	"git.snowfall.se/junction/junction/golang/raptor"
	"git.snowfall.se/junction/junction/golang/stdlib/sliceutil"
	"github.com/google/uuid"
	"github.com/uber/h3-go/v4"
	"go.uber.org/zap"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/durationpb"
	"google.golang.org/protobuf/types/known/timestamppb"
	"math"
	"sort"
	"strings"
	"time"
)

type PlannerServiceServer struct {
	planner.UnimplementedPlannerServiceServer
	Planner     *raptor.Planner
	Stops       map[h3.Cell][]*planner.Stop
	Logger      *zap.SugaredLogger
	Repository  *legacy.Repository
	WorkerCount int
}

var scheduleTypeToSegmentType map[models.Schedule_Type]v1.SegmentType

func init() {
	scheduleTypeToSegmentType = map[models.Schedule_Type]v1.SegmentType{
		models.Schedule_TYPE_UNSPECIFIED: v1.SegmentType_SEGMENT_TYPE_UNSPECIFIED,
		models.Schedule_TYPE_AIR:         v1.SegmentType_SEGMENT_TYPE_FLIGHT,
		models.Schedule_TYPE_RAIL:        v1.SegmentType_SEGMENT_TYPE_TRAIN,
		models.Schedule_TYPE_FERRY:       v1.SegmentType_SEGMENT_TYPE_FERRY,
		models.Schedule_TYPE_BUS:         v1.SegmentType_SEGMENT_TYPE_BUS,
		models.Schedule_TYPE_TAXI:        v1.SegmentType_SEGMENT_TYPE_TAXI,
		models.Schedule_TYPE_CAR:         v1.SegmentType_SEGMENT_TYPE_UNSPECIFIED,
	}
}

func difference[T comparable](a, b []T) []T {
	mb := make(map[T]struct{}, len(b))
	for _, x := range b {
		mb[x] = struct{}{}
	}
	var diff []T
	for _, x := range a {
		if _, found := mb[x]; !found {
			diff = append(diff, x)
		}
	}
	return diff
}

func (ps *PlannerServiceServer) resolveStops(wantedStops []*v1Stdlib.LatLng) []*planner.Stop {
	stops := make([]*planner.Stop, 0, len(wantedStops))

	for _, stop := range wantedStops {
		h3index := h3.LatLngToCell(h3.LatLng{
			Lat: stop.Latitude,
			Lng: stop.Longitude,
		}, 9)

		if v, ok := ps.Stops[h3index]; ok {
			stops = append(stops, v...)
		}
	}

	return stops
}

func (ps *PlannerServiceServer) resolveOriginsDestinations(wantedOrigins []*v1Stdlib.LatLng, wantedDestinations []*v1Stdlib.LatLng) ([]*planner.Stop, []*planner.Stop, error) {
	origins := ps.resolveStops(wantedOrigins)
	destinations := ps.resolveStops(wantedDestinations)
	origins = difference(origins, destinations)

	if len(origins) == 0 {
		return origins, destinations, errors.New("no suitable origins found")
	}

	destinations = difference(destinations, origins)

	if len(destinations) == 0 {
		return origins, destinations, errors.New("no suitable destinations found")
	}

	return origins, destinations, nil
}

func uniqueTimestamp(slice []*timestamppb.Timestamp) []*timestamppb.Timestamp {
	keys := make(map[string]struct{})
	list := make([]*timestamppb.Timestamp, 0, len(slice))
	for _, entry := range slice {
		if _, value := keys[entry.String()]; !value {
			keys[entry.String()] = struct{}{}
			list = append(list, entry)
		}
	}
	return list
}

func (ps *PlannerServiceServer) FindRoutes(ctx context.Context, req *planner.FindRoutesRequest) (*planner.FindRoutesResponse, error) {
	origins, destinations, err := ps.resolveOriginsDestinations(req.Origins, req.Destinations)

	if err != nil {
		return &planner.FindRoutesResponse{}, status.Error(codes.InvalidArgument, err.Error())
	}

	departureAfter := time.Now()
	departureAfter = departureAfter.AddDate(0, 0, 1)
	departureAfter = time.Date(departureAfter.Year(), departureAfter.Month(), departureAfter.Day(), 0, 0, 0, 0, time.UTC)
	departureBefore := departureAfter.AddDate(0, 0, 1)
	departureBefore = time.Date(departureBefore.Year(), departureBefore.Month(), departureBefore.Day(), 4, 0, 0, 0, departureBefore.Location())
	tripCutoff := departureAfter.Add(48 * time.Hour)

	allowedSegmentTypes := make([]models.Schedule_Type, len(req.AllowedSegmentTypes))
	copy(allowedSegmentTypes, req.AllowedSegmentTypes)

	maxConnections := -1
	if req.MaximumConnections != nil {
		maxConnections = int(*req.MaximumConnections)
	}

	results, err := ps.Planner.Search(sliceutil.Unique(origins), sliceutil.Unique(destinations), departureAfter, departureBefore, allowedSegmentTypes, maxConnections, ps.WorkerCount)

	if err != nil {
		ps.Logger.Error(err)
		return &planner.FindRoutesResponse{}, status.Error(codes.Unknown, "raptor returned an error")
	}

	a := &analyzer{
		analyzed:        make(map[string]struct{}),
		departureAfter:  departureAfter,
		departureBefore: departureBefore,
		departureTimes:  make(map[string][]time.Time),
		repository:      ps.Repository,
		tripCutoff:      tripCutoff,
	}

	for _, r := range results {
		for _, s := range r.Segments {
			if len(s.Stops) == 0 {
				continue
			}

			a.analyze(s)
		}
	}

	routesCache := make(map[string]*planner.FindRoutesResponse_Route)
	segmentsCache := make(map[string]*planner.FindRoutesResponse_Segment)

	for _, r := range results {
		routeKeyParts := make([]string, 0, len(r.Segments))

		for _, s := range r.Segments {
			if len(s.Stops) == 0 {
				continue
			}

			origin := a.repository.ScheduleStopBySequence(s.Stops[0].Sequence)
			destination := a.repository.ScheduleStopBySequence(s.Stops[len(s.Stops)-1].Sequence)
			segmentKey := makeSegmentKey(origin, destination, s.Type)
			routeKeyParts = append(routeKeyParts, segmentKey)

			if _, ok := segmentsCache[segmentKey]; ok {
				continue
			}

			originCoordinates := s.Stops[0].Cell.LatLng()
			destinationCoordinates := s.Stops[len(s.Stops)-1].Cell.LatLng()
			segmentType, ok := scheduleTypeToSegmentType[s.Type]

			if !ok {
				return &planner.FindRoutesResponse{}, status.Errorf(codes.Unknown, "unknown segment type: %d", s.Type)
			}

			departureTimes := make([]*timestamppb.Timestamp, 0, len(a.departureTimes[segmentKey]))
			dailyDepartures := uint32(0)

			for _, dt := range a.departureTimes[segmentKey] {
				departureTimes = append(departureTimes, timestamppb.New(dt))
			}

			sort.Slice(departureTimes, func(i, j int) bool {
				return departureTimes[i].Seconds < departureTimes[j].Seconds
			})

			departureTimes = uniqueTimestamp(departureTimes)

			for _, dt := range departureTimes {
				if dt.AsTime().After(departureAfter) && dt.AsTime().Before(departureBefore) {
					dailyDepartures++
				}
			}

			segment := &planner.FindRoutesResponse_Segment{
				Origin: &v1Stdlib.LatLng{
					Latitude:  originCoordinates.Lat,
					Longitude: originCoordinates.Lng,
				},
				Destination: &v1Stdlib.LatLng{
					Latitude:  destinationCoordinates.Lat,
					Longitude: destinationCoordinates.Lng,
				},
				SegmentType:              segmentType,
				EstimatedTravelTime:      durationpb.New(s.Arrive.Sub(s.Depart)),
				EstimatedDepartureTimes:  uniqueTimestamp(departureTimes),
				EstimatedDailyDepartures: dailyDepartures,
			}
			segmentsCache[segmentKey] = segment
		}

		routeKey := strings.Join(routeKeyParts, "_")
		estimatedTravelTime := durationpb.New(r.Segments[len(r.Segments)-1].Arrive.Sub(r.Segments[0].Depart))

		if v, ok := routesCache[routeKey]; ok {
			if v.EstimatedTravelTime.AsDuration() > estimatedTravelTime.AsDuration() {
				v.EstimatedTravelTime = estimatedTravelTime
			}

			continue
		}

		segments := make([]*planner.FindRoutesResponse_Segment, 0, len(routeKeyParts))
		dailyDepartures := uint32(math.MaxInt32)

		for _, s := range routeKeyParts {
			segment := segmentsCache[s]

			if segment.EstimatedDailyDepartures < dailyDepartures {
				dailyDepartures = segment.EstimatedDailyDepartures
			}

			segments = append(segments, segment)
		}

		route := &planner.FindRoutesResponse_Route{
			Segments:                 segments,
			EstimatedDailyDepartures: dailyDepartures,
			EstimatedTravelTime:      estimatedTravelTime,
		}
		routesCache[routeKey] = route
	}

	routes := make([]*planner.FindRoutesResponse_Route, 0, len(routesCache))

	for _, r := range routesCache {
		routes = append(routes, r)
	}

	return &planner.FindRoutesResponse{Routes: routes}, nil
}

func (ps *PlannerServiceServer) SearchJourney(ctx context.Context, req *planner.SearchJourneyRequest) (*planner.SearchJourneyResponse, error) {
	origins, destinations, err := ps.resolveOriginsDestinations(req.Origins, req.Destinations)

	if err != nil {
		return &planner.SearchJourneyResponse{}, status.Error(codes.InvalidArgument, err.Error())
	}

	departureTime := time.Now()

	if req.DepartureAfter != nil {
		var err error
		var originTz *time.Location

		switch v := req.DepartureAfter.TimeOffset.(type) {
		case *v1Stdlib.DateTime_TimeZone:
			originTz, err = time.LoadLocation(v.TimeZone.Id)

			if err != nil {
				return &planner.SearchJourneyResponse{}, status.Errorf(codes.Internal, "unknown time zone")
			}
		case *v1Stdlib.DateTime_UtcOffset:
			originTz = time.FixedZone("custom", int(v.UtcOffset.Seconds))
		default:
			return &planner.SearchJourneyResponse{}, status.Errorf(codes.Internal, "unknown time zone")
		}

		departureTime = time.Date(
			int(req.DepartureAfter.Year),
			time.Month(req.DepartureAfter.Month),
			int(req.DepartureAfter.Day),
			int(req.DepartureAfter.Hours),
			int(req.DepartureAfter.Minutes),
			int(req.DepartureAfter.Seconds),
			int(req.DepartureAfter.Nanos),
			originTz,
		)
	}

	var departureBefore time.Time
	if req.DepartureBefore == nil {
		eTime := departureTime.AddDate(0, 0, 1)
		departureBefore = time.Date(eTime.Year(), eTime.Month(), eTime.Day(), 4, 0, 0, 0, eTime.Location())
	} else {
		var err error
		var originTz *time.Location

		switch v := req.DepartureBefore.TimeOffset.(type) {
		case *v1Stdlib.DateTime_TimeZone:
			originTz, err = time.LoadLocation(v.TimeZone.Id)

			if err != nil {
				return &planner.SearchJourneyResponse{}, status.Errorf(codes.Internal, "unknown time zone")
			}
		case *v1Stdlib.DateTime_UtcOffset:
			originTz = time.FixedZone("custom", int(v.UtcOffset.Seconds))
		default:
			return &planner.SearchJourneyResponse{}, status.Errorf(codes.Internal, "unknown time zone")
		}

		departureBefore = time.Date(
			int(req.DepartureBefore.Year),
			time.Month(req.DepartureBefore.Month),
			int(req.DepartureBefore.Day),
			int(req.DepartureBefore.Hours),
			int(req.DepartureBefore.Minutes),
			int(req.DepartureBefore.Seconds),
			int(req.DepartureBefore.Nanos),
			originTz,
		)
	}

	allowedSegmentTypes := make([]models.Schedule_Type, len(req.AllowedSegmentTypes))
	copy(allowedSegmentTypes, req.AllowedSegmentTypes)

	maxConnections := -1
	if req.MaximumConnections != nil {
		maxConnections = int(*req.MaximumConnections)
	}

	results, err := ps.Planner.Search(sliceutil.Unique(origins), sliceutil.Unique(destinations), departureTime, departureBefore, allowedSegmentTypes, maxConnections, ps.WorkerCount)

	if err != nil {
		ps.Logger.Error(err)
		return &planner.SearchJourneyResponse{}, status.Errorf(codes.Unknown, "raptor returned an error")
	}

	trips := make([]*models.TripReference, 0, len(results))

	for _, r := range results {
		segments := make([]*models.SegmentReference, 0, len(r.Segments))

		for _, s := range r.Segments {
			if s.Id == raptor.TransferUuid {
				continue
			}

			legs := make([]string, 0, len(s.Stops)-1)

			for i := 0; i < len(s.Stops)-1; i++ {
				legs = append(legs, uuid.NewSHA1(s.ScheduleId, []byte(strings.Join([]string{
					s.Stops[i].Id,
					s.Stops[i+1].Id,
				}, "\x00"))).String(),
				)
			}

			segments = append(segments, &models.SegmentReference{
				Id:         s.Id.String(),
				ScheduleId: s.ScheduleId.String(),
				LegIds:     legs,
			})
		}

		trips = append(trips, &models.TripReference{
			Id:       r.Id.String(),
			Segments: segments,
		})
	}

	return &planner.SearchJourneyResponse{
		Trips: trips,
	}, nil
}
