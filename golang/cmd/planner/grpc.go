package main

import (
	"context"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/service/planner/v1alpha"
	models "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"
	"git.snowfall.se/junction/junction/golang/raptor"
	"github.com/google/uuid"
	"github.com/uber/h3-go"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"strings"
	"time"
)

type PlannerServiceServer struct {
	planner.UnimplementedPlannerServiceServer
	Planner *raptor.Planner
	Stops   map[h3.H3Index][]*planner.Stop
}

func (ps *PlannerServiceServer) SearchJourney(context context.Context, req *planner.SearchJourneyRequest) (*planner.SearchJourneyResponse, error) {
	if len(req.Origins) == 0 || len(req.Destinations) == 0 {
		return &planner.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "origins or destinations missing")
	}

	origins := make([]*planner.Stop, 0, len(req.Origins))
	destinations := make([]*planner.Stop, 0, len(req.Destinations))

	for _, origin := range req.Origins {
		h3index := h3.FromGeo(h3.GeoCoord{
			Latitude:  origin.Latitude,
			Longitude: origin.Longitude,
		}, 9)

		if v, ok := ps.Stops[h3index]; ok {
			origins = append(origins, v...)
		}
	}

	for _, destination := range req.Destinations {
		h3index := h3.FromGeo(h3.GeoCoord{
			Latitude:  destination.Latitude,
			Longitude: destination.Longitude,
		}, 9)

		if v, ok := ps.Stops[h3index]; ok {
			destinations = append(destinations, v...)
		}
	}

	if len(origins) == 0 {
		return &planner.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "no suitable origins found")
	}

	if len(destinations) == 0 {
		return &planner.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "no suitable destinations found")
	}

	for _, org := range origins {
		for _, dest := range destinations {
			if org.Id == dest.Id {
				return &planner.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "origins and destinations can't be the same")
			}
		}
	}

	departureTime := time.Now()

	if req.DepartureAfter != nil {
		var err error
		var originTz *time.Location

		switch v := req.DepartureAfter.TimeOffset.(type) {
		case *models.DateTime_TimeZone:
			originTz, err = time.LoadLocation(v.TimeZone.Id)

			if err != nil {
				return &planner.SearchJourneyResponse{}, status.Errorf(codes.Internal, "unknown time zone")
			}
		case *models.DateTime_UtcOffset:
			originTz = time.FixedZone("custom", int(v.UtcOffset.Seconds))
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

	results, err := ps.Planner.Search(origins, destinations, departureTime, []models.Schedule_Type{
		models.Schedule_TYPE_UNSPECIFIED,
		models.Schedule_TYPE_AIR,
		models.Schedule_TYPE_RAIL,
	})

	if err != nil {
		return &planner.SearchJourneyResponse{}, status.Errorf(codes.Unknown, "raptor returned an error")
	}

	trips := make([]*models.TripReference, 0, len(results))

	for _, r := range results {
		segments := make([]*models.SegmentReference, 0, len(r.Segments))

		for _, s := range r.Segments {
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
