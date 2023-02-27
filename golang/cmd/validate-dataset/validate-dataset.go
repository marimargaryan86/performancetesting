package main

import (
	"bufio"
	"errors"
	"fmt"
	"git.snowfall.se/junction/junction/golang/json"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/service/planner/v1alpha"
	models "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"
	"git.snowfall.se/junction/junction/golang/protoio"
	"github.com/bits-and-blooms/bloom"
	"github.com/google/uuid"
	"github.com/schollz/progressbar/v3"
	"github.com/spf13/cobra"
	"github.com/uber/h3-go/v3"
	"google.golang.org/protobuf/proto"
	"io"
	"log"
	"os"
	"path"
	"strconv"
	"strings"
)

type date struct {
	Date struct {
		NumberLong string `json:"$numberLong"`
	} `json:"$date"`
}

type point struct {
	Ref         string `json:"ref"`
	Name        string `json:"name"`
	Coordinates struct {
		Type        string    `json:"type"`
		Coordinates []float64 `json:"coordinates"`
	} `json:"coordinates"`
	TimeZone string `json:"time_zone"`
}

type leg struct {
	Id          string `json:"_id"`
	Origin      point  `json:"origin"`
	Destination point  `json:"destination"`
	DepartureAt date   `json:"departure_at"`
	ArrivalAt   date   `json:"arrival_at"`
	Type        int    `json:"type"`
	AgencyName  string `json:"agency_name"`
}

type schedule struct {
	Id         string `json:"_id"`
	Name       string `json:"name"`
	AgencyName string `json:"agency_name"`
	UpdatedAt  date   `json:"updated_at"`
	SourceRef  string `json:"source_ref"`
	Type       int    `json:"type"`
	Legs       []leg  `json:"legs"`
}

type dataset struct {
	routeStops    []*planner.RouteStop
	routes        []*planner.Route
	scheduleStops []*planner.ScheduleStop
	schedules     []*planner.Schedule
	stops         []*planner.Stop
	transfers     []*planner.Transfer
}

var cmd = &cobra.Command{
	Run:  validate,
	Args: cobra.ExactArgs(2),
}

func check(err error) {
	if err != nil {
		panic(err)
	}
}

func main() {
	if err := cmd.Execute(); err != nil {
		log.Fatal(err)
	}
}

func validate(cmd *cobra.Command, args []string) {
	d := loadProtoFiles(args[0])
	j := loadJsonSchedules(args[1])

	errors := validateSequenceNumbers(d)

	if len(errors) == 0 {
		errors = append(errors, validateSortOrder(d)...)
		errors = append(errors, validateDataIntegrity(d, j)...)
	}

	for _, err := range errors {
		log.Println(err)
	}

	if len(errors) > 0 {
		os.Exit(1)
	}
}

func loadProtoFiles(p string) dataset {
	routeStops, _ := loadProtoFile[planner.RouteStop](p, "route_stops.bin")
	routes, _ := loadProtoFile[planner.Route](p, "routes.bin")
	scheduleStops, _ := loadProtoFile[planner.ScheduleStop](p, "schedule_stops.bin")
	schedules, _ := loadProtoFile[planner.Schedule](p, "schedules.bin")
	stops, _ := loadProtoFile[planner.Stop](p, "stops.bin")
	transfers, _ := loadProtoFile[planner.Transfer](p, "transfers.bin")

	return dataset{
		routeStops,
		routes,
		scheduleStops,
		schedules,
		stops,
		transfers,
	}
}

func loadProtoFile[T any, T2 interface {
	*T
	proto.Message
}](basePath string, filename string) ([]*T, error) {
	p := path.Join(basePath, filename)
	messages := make([]*T, 0)
	f, err := os.Open(p)
	check(err)
	defer f.Close()

	stat, err := os.Stat(f.Name())
	check(err)

	if stat.Size() == 0 {
		return messages, nil
	}

	b := bufio.NewReader(f)
	progress := progressbar.NewReader(b, progressbar.DefaultBytes(
		stat.Size(),
		fmt.Sprintf("Loading %s", filename),
	))

	pr := protoio.NewProtoReader(io.Reader(&progress))

	for {
		message := new(T)

		err = pr.ReadNext(T2(message))

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

func loadJsonSchedules(p string) map[string]schedule {
	f, err := os.Open(p)
	check(err)
	defer f.Close()

	stat, err := os.Stat(f.Name())
	check(err)

	b := bufio.NewReader(f)
	progress := progressbar.NewReader(b, progressbar.DefaultBytes(
		stat.Size(),
		"Parsing JSON schedules",
	))

	schedules := make(chan schedule, 10)
	schedulesMap := make(map[string]schedule)

	go json.Stream[schedule](io.Reader(&progress), schedules)

	for s := range schedules {
		schedulesMap[s.Id] = s
	}

	return schedulesMap
}

func validateSequenceNumbers(d dataset) []error {
	progressMessage := "Validating sequence numbers"
	errors := make([]error, 0)
	bar := progressbar.Default(int64(len(d.routes)+len(d.routeStops)+len(d.stops)+len(d.transfers)+len(d.schedules)+len(d.scheduleStops)), fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))

	for sequence, r := range d.routes {
		check(bar.Add(1))

		if uint64(sequence) != r.Sequence {
			errors = append(errors, fmt.Errorf("route at sequence %d was expected at sequence %d", sequence, r.Sequence))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		for _, s := range r.Schedules {
			if uint64(len(d.schedules)) <= s {
				errors = append(errors, fmt.Errorf("route at sequence %d is referring to schedule at sequence %d which is out of range (length is %d)", sequence, s, len(d.schedules)))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			}
		}

		for _, rs := range r.RouteStops {
			if uint64(len(d.routeStops)) <= rs {
				errors = append(errors, fmt.Errorf("route at sequence %d is referring to route stop at sequence %d which is out of range (length is %d)", sequence, rs, len(d.routeStops)))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			}
		}
	}

	for sequence, rs := range d.routeStops {
		check(bar.Add(1))

		if uint64(sequence) != rs.Sequence {
			errors = append(errors, fmt.Errorf("route stop at sequence %d was expected at sequence %d", sequence, rs.Sequence))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		if uint64(len(d.routes)) <= rs.Route {
			errors = append(errors, fmt.Errorf("route stop at sequence %d is referring to route at sequence %d which is out of range (length is %d)", sequence, rs.Route, len(d.routes)))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		if uint64(len(d.stops)) <= rs.Stop {
			errors = append(errors, fmt.Errorf("route stop at sequence %d is referring to stop at sequence %d which is out of range (length is %d)", sequence, rs.Stop, len(d.stops)))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}
	}

	bloomFilter := bloom.NewWithEstimates(uint(len(d.stops)), 0.001)
	idMap := make(map[string]struct{})

	for sequence, s := range d.stops {
		check(bar.Add(1))

		if uint64(sequence) != s.Sequence {
			errors = append(errors, fmt.Errorf("stop at sequence %d was expected at sequence %d", sequence, s.Sequence))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		for _, rs := range s.RouteStops {
			if uint64(len(d.routeStops)) <= rs {
				errors = append(errors, fmt.Errorf("stop at sequence %d is referring to route stop at sequence %d which is out of range (length is %d)", sequence, rs, len(d.routeStops)))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			}
		}

		for _, ss := range s.ScheduleStops {
			if uint64(len(d.scheduleStops)) <= ss {
				errors = append(errors, fmt.Errorf("stop at sequence %d is referring to schedule stop at sequence %d which is out of range (length is %d)", sequence, ss, len(d.scheduleStops)))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			}
		}

		for _, t := range s.Transfers {
			if uint64(len(d.transfers)) <= t {
				errors = append(errors, fmt.Errorf("stop at sequence %d is referring to transfer at sequence %d which is out of range (length is %d)", sequence, t, len(d.transfers)))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			}
		}

		if found := bloomFilter.TestAndAddString(s.Id); found {
			if _, ok := idMap[s.Id]; ok {
				errors = append(errors, fmt.Errorf("stop at sequence %d has duplicated ID (%s)", sequence, s.Id))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			} else {
				idMap[s.Id] = struct{}{}
			}
		} else {
			idMap[s.Id] = struct{}{}
		}
	}

	for sequence, t := range d.transfers {
		check(bar.Add(1))

		if uint64(sequence) != t.Sequence {
			errors = append(errors, fmt.Errorf("transfer at sequence %d was expected at sequence %d", sequence, t.Sequence))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		if uint64(len(d.stops)) <= t.ToStop {
			errors = append(errors, fmt.Errorf("transfer at sequence %d is referring to stop at sequence %d which is out of range (length is %d)", sequence, t.ToStop, len(d.stops)))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		if uint64(len(d.stops)) <= t.FromStop {
			errors = append(errors, fmt.Errorf("transfer at sequence %d is referring to stop at sequence %d which is out of range (length is %d)", sequence, t.FromStop, len(d.stops)))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}
	}

	bloomFilter = bloom.NewWithEstimates(uint(len(d.schedules)), 0.001)
	idMap = make(map[string]struct{})

	for sequence, s := range d.schedules {
		check(bar.Add(1))

		if uint64(sequence) != s.Sequence {
			errors = append(errors, fmt.Errorf("schedule at sequence %d was expected at sequence %d", sequence, s.Sequence))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		if uint64(len(d.routes)) <= s.Route {
			errors = append(errors, fmt.Errorf("schedule at sequence %d is referring to route at sequence %d which is out of range (length is %d)", sequence, s.Route, len(d.routes)))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		for _, ss := range s.ScheduleStops {
			if uint64(len(d.scheduleStops)) <= ss {
				errors = append(errors, fmt.Errorf("schedule at sequence %d is referring to schedule stop at sequence %d which is out of range (length is %d)", sequence, ss, len(d.scheduleStops)))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			}
		}

		if found := bloomFilter.TestAndAddString(s.Id); found {
			if _, ok := idMap[s.Id]; ok {
				errors = append(errors, fmt.Errorf("schedule at sequence %d has duplicated ID (%s)", sequence, s.Id))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			} else {
				idMap[s.Id] = struct{}{}
			}
		} else {
			idMap[s.Id] = struct{}{}
		}
	}

	bloomFilter = bloom.NewWithEstimates(uint(len(d.scheduleStops)), 0.001)
	idMap = make(map[string]struct{})

	for sequence, ss := range d.scheduleStops {
		check(bar.Add(1))

		if uint64(sequence) != ss.Sequence {
			errors = append(errors, fmt.Errorf("schedule stop at sequence %d was expected at sequence %d", sequence, ss.Sequence))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		if uint64(len(d.schedules)) <= ss.Schedule {
			errors = append(errors, fmt.Errorf("schedule stop at sequence %d is referring to schedule at sequence %d which is out of range (length is %d)", sequence, ss.Schedule, len(d.schedules)))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		if uint64(len(d.stops)) <= ss.Stop {
			errors = append(errors, fmt.Errorf("schedule stop at sequence %d is referring to stop at sequence %d which is out of range (length is %d)", sequence, ss.Stop, len(d.stops)))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		if found := bloomFilter.TestAndAddString(ss.Id); found {
			if _, ok := idMap[ss.Id]; ok {
				errors = append(errors, fmt.Errorf("schedule stop at sequence %d has duplicated ID (%s)", sequence, ss.Id))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			} else {
				idMap[ss.Id] = struct{}{}
			}
		} else {
			idMap[ss.Id] = struct{}{}
		}
	}

	check(bar.Finish())

	return errors
}

func validateSortOrder(d dataset) []error {
	progressMessage := "Validating sort order"
	errors := make([]error, 0)
	bar := progressbar.Default(int64(len(d.routes)+len(d.stops)), fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))

	for sequence, r := range d.routes {
		check(bar.Add(1))

		for i := 1; i < len(r.Schedules); i++ {
			if d.scheduleStops[d.schedules[r.Schedules[i]].ScheduleStops[0]].DepartureAt < d.scheduleStops[d.schedules[r.Schedules[i-1]].ScheduleStops[0]].DepartureAt {
				errors = append(errors, fmt.Errorf("route at sequence %d does not have its schedules sorted correctly", sequence))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			}
		}
	}

	for sequence, s := range d.stops {
		check(bar.Add(1))

		for i := 1; i < len(s.ScheduleStops); i++ {
			if d.scheduleStops[s.ScheduleStops[i]].DepartureAt < d.scheduleStops[s.ScheduleStops[i-1]].DepartureAt {
				errors = append(errors, fmt.Errorf("stop at sequence %d does not have its schedule stops sorted correctly", sequence))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			}
		}
	}

	check(bar.Finish())

	return errors
}

func validateDataIntegrity(d dataset, sm map[string]schedule) []error {
	pSchedulesMap := make(map[string]*planner.Schedule, len(d.schedules))

	for _, ps := range d.schedules {
		pSchedulesMap[ps.Id] = ps
	}

	progressMessage := "Validating data integrity"
	errors := make([]error, 0)
	bar := progressbar.Default(int64(len(sm)), fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))

	for _, js := range sm {
		check(bar.Add(1))

		ps, ok := pSchedulesMap[js.Id]

		if !ok {
			errors = append(errors, fmt.Errorf("schedule with ID %s from protobuf not found in JSON", js.Id))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			continue
		}

		legs := make([][2]*planner.ScheduleStop, 0, len(ps.ScheduleStops)-1)
		pScheduleId, err := uuid.Parse(ps.Id)

		if err != nil {
			errors = append(errors, fmt.Errorf("schedule at sequence %d does not have a UUID as ID (%s): %s", ps.Sequence, ps.Id, err))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		} else {
			for i := 0; i < len(ps.ScheduleStops); i++ {
				stopId := uuid.NewSHA1(pScheduleId, []byte(strconv.Itoa(i)))

				if d.scheduleStops[ps.ScheduleStops[i]].Id != stopId.String() {
					errors = append(errors, fmt.Errorf("schedule stop at sequence %d has an invalid ID (%s found, %s expected)", d.scheduleStops[ps.ScheduleStops[i]].Sequence, d.scheduleStops[ps.ScheduleStops[i]].Id, stopId.String()))
					bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
				}

				if i != len(ps.ScheduleStops)-1 {
					legs = append(legs, [2]*planner.ScheduleStop{
						d.scheduleStops[ps.ScheduleStops[i]],
						d.scheduleStops[ps.ScheduleStops[i+1]],
					})
				}
			}

			for i, l := range js.Legs {
				originIndex := h3.FromGeo(h3.GeoCoord{
					Latitude:  l.Origin.Coordinates.Coordinates[1],
					Longitude: l.Origin.Coordinates.Coordinates[0],
				}, 9)

				destinationIndex := h3.FromGeo(h3.GeoCoord{
					Latitude:  l.Destination.Coordinates.Coordinates[1],
					Longitude: l.Destination.Coordinates.Coordinates[0],
				}, 9)

				originId, err := strconv.Atoi(d.stops[legs[i][0].Stop].Id)
				destinationId, err2 := strconv.Atoi(d.stops[legs[i][1].Stop].Id)

				if err != nil {
					errors = append(errors, fmt.Errorf("stop at sequence %d does not have a H3Index as ID (%s): %s", d.stops[legs[i][0].Stop].Sequence, d.stops[legs[i][0].Stop].Id, err))
					bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
				} else if uint64(originId) != uint64(originIndex) {
					errors = append(errors, fmt.Errorf("stop at sequence %d has an invalid ID (%d found, %d expected)", d.stops[legs[i][0].Stop].Sequence, originId, uint64(originIndex)))
					bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
				}

				if err2 != nil {
					errors = append(errors, fmt.Errorf("stop at sequence %d does not have a H3Index as ID (%s): %s", d.stops[legs[i][1].Stop].Sequence, d.stops[legs[i][1].Stop].Id, err2))
					bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
				} else if uint64(destinationId) != uint64(destinationIndex) {
					errors = append(errors, fmt.Errorf("stop at sequence %d has an invalid ID (%d found, %d expected)", d.stops[legs[i][1].Stop].Sequence, destinationId, uint64(destinationIndex)))
					bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
				}

				firstStopId, err := uuid.Parse(legs[i][0].Id)

				if err != nil {
					errors = append(errors, fmt.Errorf("schedule stop at sequence %d does not have a UUID as ID (%s): %s", legs[i][0].Sequence, legs[i][0].Id, err))
					bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
				}

				secondStopId, err2 := uuid.Parse(legs[i][1].Id)

				if err2 != nil {
					errors = append(errors, fmt.Errorf("schedule stop at sequence %d does not have a UUID as ID (%s): %s", legs[i][1].Sequence, legs[i][1].Id, err2))
					bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
				}

				if err == nil && err2 == nil {
					pLegId := uuid.NewSHA1(pScheduleId, []byte(
						strings.Join([]string{
							firstStopId.String(),
							secondStopId.String(),
						}, "\x00"),
					))

					if l.Id != pLegId.String() {
						errors = append(errors, fmt.Errorf("IDs for leg #%d in schedule %s do not match (%s in protobuf, %s in JSON)", i, pScheduleId.String(), l.Id, pLegId.String()))
						bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
					}
				}
			}
		}

		jScheduleId, err := uuid.Parse(js.Id)

		if err != nil {
			errors = append(errors, fmt.Errorf("schedule in JSON does not have a UUID as ID (%s): %s", js.Id, err))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		} else {
			for i, l := range js.Legs {
				jLegId := uuid.NewSHA1(jScheduleId, []byte(
					strings.Join([]string{
						uuid.NewSHA1(jScheduleId, []byte(strconv.Itoa(i))).String(),
						uuid.NewSHA1(jScheduleId, []byte(strconv.Itoa(i+1))).String(),
					}, "\x00")))

				if l.Id != jLegId.String() {
					errors = append(errors, fmt.Errorf("ID for leg #%d in schedule %s has an invalid ID (%s found, %s expected)", i, jScheduleId.String(), l.Id, jLegId.String()))
					bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
				}
			}
		}

		if _, ok := models.Schedule_Type_name[int32(js.Type)]; !ok {
			errors = append(errors, fmt.Errorf("type for schedule %s is not a valid (%d)", js.Id, js.Type))
			bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
		}

		for i, l := range js.Legs {
			if js.Type != l.Type {
				errors = append(errors, fmt.Errorf("type for leg #%d in schedule %s does not match type of schedule (%d found, %d expected)", i, js.Id, l.Type, js.Type))
				bar.Describe(fmt.Sprintf("%s (%d errors)", progressMessage, len(errors)))
			}
		}
	}

	check(bar.Finish())

	return errors
}
