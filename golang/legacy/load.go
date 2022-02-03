package legacy

import (
	"bufio"
	"errors"
	"fmt"
	"git.snowfall.se/junction/junction/golang/protoio"
	"go.uber.org/zap"
	"google.golang.org/protobuf/proto"
	"io"
	"os"
	"path/filepath"
	"reflect"
)

// Load loads a protobuf-based data structure from disk into memory.
func Load(logger *zap.SugaredLogger, from string) ([]*Route, []*RouteSegment, []*Stop, []*Transfer, []*Trip, []*TripSegment, error) {
	var routes []*Route
	var routeSegments []*RouteSegment
	var stops []*Stop
	var transfers []*Transfer
	var trips []*Trip
	var tripSegments []*TripSegment

	messages, err := load(filepath.Join(from, "routes.bin"), reflect.TypeOf(Route{}))
	if err != nil {
		return routes, routeSegments, stops, transfers, trips, tripSegments, err
	}

	routes = make([]*Route, len(messages))

	for i := 0; i < len(messages); i++ {
		routes[i] = messages[i].(*Route)
	}

	logger.Infow("file loaded", "file", "routes.bin")

	messages, err = load(filepath.Join(from, "route_segments.bin"), reflect.TypeOf(RouteSegment{}))

	if err != nil {
		return routes, routeSegments, stops, transfers, trips, tripSegments, err
	}

	routeSegments = make([]*RouteSegment, len(messages))

	for i := 0; i < len(messages); i++ {
		routeSegments[i] = messages[i].(*RouteSegment)
	}

	logger.Infow("file loaded", "file", "route_segments.bin")

	messages, err = load(filepath.Join(from, "stops.bin"), reflect.TypeOf(Stop{}))

	if err != nil {
		return routes, routeSegments, stops, transfers, trips, tripSegments, err
	}

	stops = make([]*Stop, len(messages))

	for i := 0; i < len(messages); i++ {
		stops[i] = messages[i].(*Stop)
	}

	logger.Infow("file loaded", "file", "stops.bin")

	messages, err = load(filepath.Join(from, "transfers.bin"), reflect.TypeOf(Transfer{}))

	if err != nil {
		return routes, routeSegments, stops, transfers, trips, tripSegments, err
	}

	transfers = make([]*Transfer, len(messages))

	for i := 0; i < len(messages); i++ {
		transfers[i] = messages[i].(*Transfer)
	}

	logger.Infow("file loaded", "file", "transfers.bin")

	messages, err = load(filepath.Join(from, "trips.bin"), reflect.TypeOf(Trip{}))

	if err != nil {
		return routes, routeSegments, stops, transfers, trips, tripSegments, err
	}

	trips = make([]*Trip, len(messages))

	for i := 0; i < len(messages); i++ {
		trips[i] = messages[i].(*Trip)
	}

	logger.Infow("file loaded", "file", "trips.bin")

	messages, err = load(filepath.Join(from, "trip_segments.bin"), reflect.TypeOf(TripSegment{}))

	if err != nil {
		return routes, routeSegments, stops, transfers, trips, tripSegments, err
	}

	tripSegments = make([]*TripSegment, len(messages))

	for i := 0; i < len(messages); i++ {
		tripSegments[i] = messages[i].(*TripSegment)
	}

	logger.Infow("file loaded", "file", "trip_segments.bin")

	return routes, routeSegments, stops, transfers, trips, tripSegments, nil
}

func load(filepath string, t reflect.Type) (messages []proto.Message, err error) {
	f, err := os.Open(filepath)
	if err != nil {
		return messages, fmt.Errorf("unable to open file: %w", err)
	}

	defer f.Close()

	pr := protoio.NewProtoReader(bufio.NewReader(f))
	messages = make([]proto.Message, 0)

	for {
		message := reflect.New(t).Interface().(proto.Message)
		err = pr.ReadNext(message)

		if errors.Is(err, io.EOF) {
			break
		}

		if err != nil {
			return messages, err
		}

		messages = append(messages, message)
	}

	return messages, nil
}
