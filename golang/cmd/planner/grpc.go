package main

import (
	"context"
	"git.snowfall.se/junction/junction/golang/legacy"
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
	Stops   map[h3.H3Index][]*legacy.Stop
}

func (ps *PlannerServiceServer) SearchJourney(context context.Context, req *planner.SearchJourneyRequest) (*planner.SearchJourneyResponse, error) {
	origins := make([]*legacy.Stop, 0)
	destinations := make([]*legacy.Stop, 0)
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

	results, err := ps.Planner.Search(origins, destinations, departureTime, []legacy.Trip_Kind{
		legacy.Trip_KIND_UNSPECIFIED,
		legacy.Trip_KIND_AIR,
		legacy.Trip_KIND_RAIL,
		legacy.Trip_KIND_WALK,
	})

	if err != nil {
		return &planner.SearchJourneyResponse{}, status.Errorf(codes.Unknown, "raptor returned an error")
	}

	trips := make([]*models.TripReference, 0, len(results))

	for _, r := range results {
		segments := make([]*models.SegmentReference, 0, len(r.Segments))

		for _, s := range r.Segments {
			legs := make([]*models.StopReference, 0, len(s.Legs))

			for _, l := range s.Legs {
				legs = append(legs, &models.StopReference{
					Id: l.Id.String(),
				})
			}

			segments = append(segments, &models.SegmentReference{
				Id:    s.Id.String(),
				Stops: legs,
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
