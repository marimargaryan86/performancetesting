package main

import (
	"context"
	models "git.snowfall.se/junction/junction/golang/protobuf/snowfall/common/v1alpha"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/junction/planner/v1alpha"
	"git.snowfall.se/junction/junction/golang/raptor"
	"github.com/uber/h3-go"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"time"
)

type PlannerServiceServer struct {
	planner.UnimplementedPlannerServiceServer
	Planner *raptor.Planner
	Stops   map[h3.H3Index][]*planner.Stop
}

func (ps *PlannerServiceServer) SearchJourney(context context.Context, req *planner.SearchJourneyRequest) (*planner.SearchJourneyResponse, error) {
	origins := make([]*planner.Stop, 0)
	destinations := make([]*planner.Stop, 0)
	origin := h3.FromGeo(h3.GeoCoord{
		Latitude:  req.Origin.Latitude,
		Longitude: req.Origin.Longitude,
	}, 9)
	destination := h3.FromGeo(h3.GeoCoord{
		Latitude:  req.Destination.Latitude,
		Longitude: req.Destination.Longitude,
	}, 9)

	if _, ok := ps.Stops[origin]; !ok {
		return &planner.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "no suitable origins found")
	}

	if _, ok := ps.Stops[destination]; !ok {
		return &planner.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "no suitable destinations found")
	}

	for _, org := range ps.Stops[origin] {
		for _, dest := range ps.Stops[destination] {
			if org.Id == dest.Id {
				return &planner.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "origin or destination can't be the same")
			}
		}

		origins = append(origins, org)
	}

	destinations = append(destinations, ps.Stops[destination]...)
	minDeparture := time.Now()
	maxDeparture := minDeparture.Add(24 * 90 * time.Hour)
	departureTime := time.Unix(req.DepartureAfter, 0)

	if departureTime.Before(minDeparture) || departureTime.After(maxDeparture) {
		return &planner.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "invalid departure time")
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
			segments = append(segments, &models.SegmentReference{
				Id:                s.Id.String(),
				ScheduleId:        s.ScheduleId.String(),
				OriginStopId:      s.Legs[0].Id.String(),
				DestinationStopId: s.Legs[len(s.Legs)-1].Id.String(),
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
