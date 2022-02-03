package main

import (
	"context"
	"git.snowfall.se/junction/junction/golang/legacy"
	plannerv1 "git.snowfall.se/junction/junction/golang/protobuf/snowfall/junction/planner/v1"
	"git.snowfall.se/junction/junction/golang/raptor"
	"github.com/uber/h3-go"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"time"
)

type PlannerServiceServer struct {
	plannerv1.UnimplementedPlannerServiceServer
	Planner *raptor.Planner
	Stops   map[h3.H3Index][]*legacy.Stop
}

func (ps *PlannerServiceServer) SearchJourney(context context.Context, req *plannerv1.SearchJourneyRequest) (*plannerv1.SearchJourneyResponse, error) {
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
		return &plannerv1.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "no suitable origins found")
	}

	if _, ok := ps.Stops[destination]; !ok {
		return &plannerv1.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "no suitable destinations found")
	}

	for _, org := range ps.Stops[origin] {
		for _, dest := range ps.Stops[destination] {
			if org.Id == dest.Id {
				return &plannerv1.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "origin or destination can't be the same")
			}
		}

		origins = append(origins, org)
	}

	destinations = append(destinations, ps.Stops[destination]...)
	minDeparture := time.Now()
	maxDeparture := minDeparture.Add(24 * 90 * time.Hour)
	departureTime := time.Unix(req.DepartureAfter, 0)

	if departureTime.Before(minDeparture) || departureTime.After(maxDeparture) {
		return &plannerv1.SearchJourneyResponse{}, status.Errorf(codes.InvalidArgument, "invalid departure time")
	}

	results, err := ps.Planner.Search(origins, destinations, departureTime, []legacy.Trip_Kind{
		legacy.Trip_KIND_UNSPECIFIED,
		legacy.Trip_KIND_AIR,
		legacy.Trip_KIND_RAIL,
		legacy.Trip_KIND_WALK,
	})

	if err != nil {
		return &plannerv1.SearchJourneyResponse{}, status.Errorf(codes.Unknown, "raptor returned an error")
	}

	trips := make([]*plannerv1.TripReference, 0, len(results))

	for _, r := range results {
		segments := make([]*plannerv1.SegmentReference, 0, len(r.Segments))

		for _, s := range r.Segments {
			legs := make([]*plannerv1.LegReference, 0, len(s.Legs))

			for _, l := range s.Legs {
				legs = append(legs, &plannerv1.LegReference{
					Id: l.Id.String(),
				})
			}

			segments = append(segments, &plannerv1.SegmentReference{
				Id:   s.Id.String(),
				Legs: legs,
			})
		}

		trips = append(trips, &plannerv1.TripReference{
			Id:       r.Id.String(),
			Segments: segments,
		})
	}

	return &plannerv1.SearchJourneyResponse{
		Trips: trips,
	}, nil
}
