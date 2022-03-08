package legacy

import (
	"bufio"
	"errors"
	"fmt"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/junction/planner/v1alpha"
	"git.snowfall.se/junction/junction/golang/protoio"
	"go.uber.org/zap"
	"google.golang.org/protobuf/proto"
	"io"
	"os"
	"path/filepath"
	"reflect"
)

// Load loads a protobuf-based data structure from disk into memory.
func Load(logger *zap.SugaredLogger, from string) ([]*planner.Route, []*planner.RouteStop, []*planner.Stop, []*planner.Transfer, []*planner.Schedule, []*planner.ScheduleStop, error) {
	var routes []*planner.Route
	var routeStops []*planner.RouteStop
	var stops []*planner.Stop
	var transfers []*planner.Transfer
	var schedules []*planner.Schedule
	var scheduleStops []*planner.ScheduleStop

	messages, err := load(filepath.Join(from, "routes.bin"), reflect.TypeOf(planner.Route{}))
	if err != nil {
		return routes, routeStops, stops, transfers, schedules, scheduleStops, err
	}

	routes = make([]*planner.Route, len(messages))

	for i := 0; i < len(messages); i++ {
		routes[i] = messages[i].(*planner.Route)
	}

	logger.Infow("file loaded", "file", "routes.bin")

	messages, err = load(filepath.Join(from, "route_stops.bin"), reflect.TypeOf(planner.RouteStop{}))

	if err != nil {
		return routes, routeStops, stops, transfers, schedules, scheduleStops, err
	}

	routeStops = make([]*planner.RouteStop, len(messages))

	for i := 0; i < len(messages); i++ {
		routeStops[i] = messages[i].(*planner.RouteStop)
	}

	logger.Infow("file loaded", "file", "route_stops.bin")

	messages, err = load(filepath.Join(from, "stops.bin"), reflect.TypeOf(planner.Stop{}))

	if err != nil {
		return routes, routeStops, stops, transfers, schedules, scheduleStops, err
	}

	stops = make([]*planner.Stop, len(messages))

	for i := 0; i < len(messages); i++ {
		stops[i] = messages[i].(*planner.Stop)
	}

	logger.Infow("file loaded", "file", "stops.bin")

	messages, err = load(filepath.Join(from, "transfers.bin"), reflect.TypeOf(planner.Transfer{}))

	if err != nil {
		return routes, routeStops, stops, transfers, schedules, scheduleStops, err
	}

	transfers = make([]*planner.Transfer, len(messages))

	for i := 0; i < len(messages); i++ {
		transfers[i] = messages[i].(*planner.Transfer)
	}

	logger.Infow("file loaded", "file", "transfers.bin")

	messages, err = load(filepath.Join(from, "schedules.bin"), reflect.TypeOf(planner.Schedule{}))

	if err != nil {
		return routes, routeStops, stops, transfers, schedules, scheduleStops, err
	}

	schedules = make([]*planner.Schedule, len(messages))

	for i := 0; i < len(messages); i++ {
		schedules[i] = messages[i].(*planner.Schedule)
	}

	logger.Infow("file loaded", "file", "schedules.bin")

	messages, err = load(filepath.Join(from, "schedule_stops.bin"), reflect.TypeOf(planner.ScheduleStop{}))

	if err != nil {
		return routes, routeStops, stops, transfers, schedules, scheduleStops, err
	}

	scheduleStops = make([]*planner.ScheduleStop, len(messages))

	for i := 0; i < len(messages); i++ {
		scheduleStops[i] = messages[i].(*planner.ScheduleStop)
	}

	logger.Infow("file loaded", "file", "schedule_stops.bin")

	return routes, routeStops, stops, transfers, schedules, scheduleStops, nil
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
