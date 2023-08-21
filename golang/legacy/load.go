package legacy

import (
	"bufio"
	"errors"
	"fmt"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/go/service/planner/v1"
	"git.snowfall.se/junction/junction/golang/protoio"
	"go.uber.org/zap"
	"google.golang.org/protobuf/proto"
	"io"
	"os"
	"path/filepath"
)

// Load loads a protobuf-based data structure from disk into memory.
func Load(logger *zap.SugaredLogger, from string) (routes []*planner.Route, routeStops []*planner.RouteStop, stops []*planner.Stop, transfers []*planner.Transfer, schedules []*planner.Schedule, scheduleStops []*planner.ScheduleStop, err error) {
	routes, err = load[planner.Route](filepath.Join(from, "routes.bin"), logger)
	if err != nil {
		return
	}

	routeStops, err = load[planner.RouteStop](filepath.Join(from, "route_stops.bin"), logger)
	if err != nil {
		return
	}

	stops, err = load[planner.Stop](filepath.Join(from, "stops.bin"), logger)
	if err != nil {
		return
	}

	transfers, err = load[planner.Transfer](filepath.Join(from, "transfers.bin"), logger)
	if err != nil {
		return
	}

	schedules, err = load[planner.Schedule](filepath.Join(from, "schedules.bin"), logger)
	if err != nil {
		return
	}

	scheduleStops, err = load[planner.ScheduleStop](filepath.Join(from, "schedule_stops.bin"), logger)
	if err != nil {
		return
	}

	return
}

type protoMessage[T any] interface {
	*T
	proto.Message
}

func load[T any, U protoMessage[T]](path string, logger *zap.SugaredLogger) (messages []U, err error) {
	f, err := os.Open(path)
	if err != nil {
		return messages, fmt.Errorf("unable to open file: %w", err)
	}

	defer f.Close()

	pr := protoio.NewProtoReader[U](bufio.NewReader(f))
	messages = make([]U, 0)

	for {
		message := new(T)
		err = pr.ReadNext(U(message))

		if errors.Is(err, io.EOF) {
			break
		}

		if err != nil {
			return messages, err
		}

		messages = append(messages, message)
	}

	logger.Infow("file loaded", "file", filepath.Base(path))

	return messages, nil
}
