package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"math"
	"os"
	"path"
	"reflect"
	"strconv"
	"strings"
	"time"

	"git.snowfall.se/junction/junction/golang/json"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/go/service/planner/v1alpha"
	//models "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"
	"git.snowfall.se/junction/junction/golang/protoio"
	"github.com/bits-and-blooms/bloom"
	"github.com/google/uuid"
	"github.com/schollz/progressbar/v3"
	"github.com/spf13/cobra"
	//"github.com/uber/h3-go"
	"google.golang.org/protobuf/proto"
)

/*
cmd/validate-dataset/validate-dataset.go
Requires 3 positional parameters, run as:
go run validate-dataset.go <data_root>/export-data schedules.bson locations.bson

WHERE
output_data is the location for the 6 scheduler BIN files from the export step.
schedules.bson and locations.bson from the import step.

AND
accepts one env var VALIDATE_DATASET_COVERAGE
a number between 1 and 100 giving the %coverage of the  data that should be
tested. Assume 100% if env var is missing or not a valid number
*/

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

type location struct {
	Id          string `json:"_id"`
	Name        string `json:"name"`
	Coordinates struct {
		Type        string    `json:"type"`
		Coordinates []float64 `json:"coordinates"`
	} `json:"coordinates"`
	TimeZone  string  `json:"time_zone"`
	UpdatedAt date    `json:"updated_at"`
	SourceRef string  `json:"source_ref"`
	Types     []int64 `json:"types"`
}

type dataset struct {
	routeStops    <-chan *planner.RouteStop
	routes        <-chan *planner.Route
	scheduleStops <-chan *planner.ScheduleStop
	schedules     <-chan *planner.Schedule
	stops         <-chan *planner.Stop
	transfers     <-chan *planner.Transfer
}

var cmd = &cobra.Command{
	Run:  validate,
	Args: cobra.ExactArgs(3),
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

func validate(_ *cobra.Command, args []string) {
	// Get sizes for each input file.
	data, err := ioutil.ReadFile(path.Join(args[0], "_sizes"))
	check(err)
	sizes := make(map[string]uint64)
	for _, line := range strings.Split(string(data), "\n") {
		if line == "" {
			continue
		}
		row := strings.SplitN(line, " ", 2)

		sizes[row[0]], err = strconv.ParseUint(row[1], 10, 64)
		check(err)
	}

	d := loadProtoReaders(args[0])
	v := reflect.ValueOf(d)
	typeOfD := v.Type()
	for i := 0; i < v.NumField(); i++ {
		k := typeOfD.Field(i).Name
		if _, ok := sizes[k]; !ok {
			panic(fmt.Errorf("Missing size for file %s", k))
		}
	}

	objFile, err := os.Open(args[1])
	check(err)
	defer objFile.Close()

	locationsFile, err := os.Open(args[2])
	check(err)
	defer locationsFile.Close()
	validateLocationFile(locationsFile)

	validateSequenceNumbers(d, sizes, loadObjSchedules(objFile))
}

func validateLocationFile(f *os.File) {
	b := bufio.NewReader(f)

	locations := make(chan location)
	locationsMap := make(map[string]location)

	go json.BSONStream[location](io.Reader(b), locations)

	found := false
	for l := range locations {
		if match, ok := locationsMap[l.Id]; ok {
			// Ensure any duplicates are exact matches.
			if !reflect.DeepEqual(match, l) {
				panic("Duplicate ID found in locations.")
			}
		}
		locationsMap[l.Id] = l
		found = true
	}
	if !found {
		panic("No locations found.")
	}
}

func loadProtoReaders(p string) dataset {
	routeStops := createProtoReader[planner.RouteStop](p, "route_stops.bin")
	routes := createProtoReader[planner.Route](p, "routes.bin")
	scheduleStops := createProtoReader[planner.ScheduleStop](p, "schedule_stops.bin")
	schedules := createProtoReader[planner.Schedule](p, "schedules.bin")
	stops := createProtoReader[planner.Stop](p, "stops.bin")
	transfers := createProtoReader[planner.Transfer](p, "transfers.bin")

	return dataset{
		routeStops,
		routes,
		scheduleStops,
		schedules,
		stops,
		transfers,
	}
}

func progress(size int64, msg string) *progressbar.ProgressBar {
	return progressbar.NewOptions64(size,
		// Options for DefaultBytes with Throttle changed to limit logging on Gitlab.
		progressbar.OptionSetDescription(msg),
		progressbar.OptionSetWriter(os.Stderr),
		progressbar.OptionShowBytes(true),
		progressbar.OptionSetWidth(10),
		progressbar.OptionThrottle(60*time.Second),
		progressbar.OptionShowCount(),
		progressbar.OptionOnCompletion(func() {
			fmt.Fprint(os.Stderr, "\n")
		}),
		progressbar.OptionSpinnerType(14),
		progressbar.OptionFullWidth(),
		progressbar.OptionSetRenderBlankState(true),
	)
}

func createProtoReader[T any, T2 interface {
	*T
	proto.Message
}](basePath string, filename string) <-chan *T {
	ch := make(chan *T)
	p := path.Join(basePath, filename)

	go func() {
		f, err := os.Open(p)
		check(err)
		defer f.Close()

		stat, err := f.Stat()
		check(err)

		b := bufio.NewReader(f)
		progress := progressbar.NewReader(b, progress(stat.Size(), filename))

		pr := protoio.NewProtoReader[T2](io.Reader(&progress))

		for {
			message := new(T)

			err = pr.ReadNext(T2(message))
			if errors.Is(err, io.EOF) {
				break
			}
			if err != nil {
				panic(err)
			}

			ch <- message
		}
		close(ch)
	}()

	return ch
}

func loadObjSchedules(f *os.File) chan schedule {
	//stat, err := os.Stat(f.Name())
	//check(err)

	b := bufio.NewReader(f)
	//progress := progressbar.NewReader(b, progress(stat.Size(), "Parsing JSON schedules"))

	schedules := make(chan schedule, 10)
	//schedulesMap := make(map[string]schedule)

	go json.BSONStream[schedule](b, schedules)

	//for s := range schedules {
	//	schedulesMap[s.Id] = s
	//}

	return schedules
}

func calculateBloomProbability(size uint64) float64 {
	// Calculate probability needed per item such that there is a 1% probability of a
	// false positive across the entire dataset.
	// i.e. This script is 99% likely to pass when given a valid dataset.
	// This seems to use just over 5% of the RAM needed when using a map/set.
	return 1 - (math.Pow(0.99, (float64(1) / float64(size))))
}

func validateSequenceNumbers(d dataset, sizes map[string]uint64, objSchedules chan schedule) {
	// Careful with changes here, these arrays use a huge amount of memory.
	departAtScheduleStops := make([]uint32, sizes["scheduleStops"], sizes["scheduleStops"]) // >1 GB
	idsScheduleStops := make([][16]byte, sizes["scheduleStops"], sizes["scheduleStops"])    // >4 GB

	bloomFilter := bloom.NewWithEstimates(uint(sizes["scheduleStops"]), calculateBloomProbability(sizes["scheduleStops"]))
	var last_ss *planner.ScheduleStop
	for ss := range d.scheduleStops {
		if last_ss == nil {
			if ss.Sequence != 0 {
				panic(fmt.Errorf("schedule stop at sequence %d was expected at sequence %d", 0, ss.Sequence))
			}
		} else if ss.Sequence != last_ss.Sequence+1 {
			panic(fmt.Errorf("schedule stop at sequence %d was expected at sequence %d", last_ss.Sequence+1, ss.Sequence))
		}

		if ss.Schedule >= sizes["schedules"] {
			panic(fmt.Errorf("schedule stop at sequence %d is referring to schedule at sequence %d which is out of range (length is %d)", ss.Sequence, ss.Schedule, len(d.schedules)))
		}

		if ss.Stop >= sizes["stops"] {
			panic(fmt.Errorf("schedule stop at sequence %d is referring to stop at sequence %d which is out of range (length is %d)", ss.Sequence, ss.Stop, len(d.stops)))
		}

		if bloomFilter.TestAndAddString(ss.Id) {
			panic(fmt.Errorf("schedule stop at sequence %d has duplicated ID (%s)", ss.Sequence, ss.Id))
		}

		departAtScheduleStops[ss.Sequence] = ss.DepartureAt
		uuid, err := uuid.Parse(ss.Id)
		check(err)
		idsScheduleStops[ss.Sequence] = uuid
		last_ss = ss
	}
	if last_ss.Sequence != sizes["scheduleStops"]-1 {
		panic(fmt.Errorf("Wrong schedule_stops count %s, expected %s", last_ss.Sequence, sizes["scheduleStops"]-1))
	}

	departAtSchedules := make([]uint32, sizes["schedules"])
	bloomFilter = bloom.NewWithEstimates(uint(sizes["schedules"]), calculateBloomProbability(sizes["schedules"]))
	var last_sc *planner.Schedule
	for s := range d.schedules {
		objSchedule := <-objSchedules

		if s.Id != objSchedule.Id {
			panic(fmt.Errorf("schedule with ID %s from protobuf not found in object file", objSchedule.Id))
		}

		pScheduleId, err := uuid.Parse(s.Id)
		if err != nil {
			panic(fmt.Errorf("schedule at sequence %d does not have a UUID as ID (%s): %s", s.Sequence, s.Id, err))
		}

		for i, ss := range s.ScheduleStops {
			stopId := uuid.NewSHA1(pScheduleId, []byte(strconv.Itoa(i)))
			if idsScheduleStops[ss] != stopId {
				panic(fmt.Errorf("schedule stop at sequence %d has an invalid ID (%s found, %s expected)", ss, idsScheduleStops[ss], stopId.String()))
			}

			if i != len(s.ScheduleStops)-1 {
				//legs = append(legs, [2]*planner.ScheduleStop{
				//	d.scheduleStops[ss],
				//	d.scheduleStops[s.ScheduleStops[i+1]],
				//})
			}
		}

		/*for i, l := range objSchedule.Legs {
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
				dataErrors = append(dataErrors, fmt.Errorf("stop at sequence %d does not have a H3Index as ID (%s): %s", d.stops[legs[i][0].Stop].Sequence, d.stops[legs[i][0].Stop].Id, err))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			} else if uint64(originId) != uint64(originIndex) {
				dataErrors = append(dataErrors, fmt.Errorf("stop at sequence %d has an invalid ID (%d found, %d expected)", d.stops[legs[i][0].Stop].Sequence, originId, uint64(originIndex)))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			}

			if err2 != nil {
				dataErrors = append(dataErrors, fmt.Errorf("stop at sequence %d does not have a H3Index as ID (%s): %s", d.stops[legs[i][1].Stop].Sequence, d.stops[legs[i][1].Stop].Id, err2))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			} else if uint64(destinationId) != uint64(destinationIndex) {
				dataErrors = append(dataErrors, fmt.Errorf("stop at sequence %d has an invalid ID (%d found, %d expected)", d.stops[legs[i][1].Stop].Sequence, destinationId, uint64(destinationIndex)))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			}

			firstStopId, err := uuid.Parse(legs[i][0].Id)

			if err != nil {
				dataErrors = append(dataErrors, fmt.Errorf("schedule stop at sequence %d does not have a UUID as ID (%s): %s", legs[i][0].Sequence, legs[i][0].Id, err))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			}

			secondStopId, err2 := uuid.Parse(legs[i][1].Id)

			if err2 != nil {
				dataErrors = append(dataErrors, fmt.Errorf("schedule stop at sequence %d does not have a UUID as ID (%s): %s", legs[i][1].Sequence, legs[i][1].Id, err2))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			}

			if err == nil && err2 == nil {
				pLegId := uuid.NewSHA1(pScheduleId, []byte(
					strings.Join([]string{
						firstStopId.String(),
						secondStopId.String(),
					}, "\x00"),
				))

				if l.Id != pLegId.String() {
					dataErrors = append(dataErrors, fmt.Errorf("IDs for leg #%d in schedule %s do not match (%s in protobuf, %s in JSON)", i, pScheduleId.String(), l.Id, pLegId.String()))
					bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
				}
			}
		}*/

		if last_sc == nil {
			if s.Sequence != 0 {
				panic(fmt.Errorf("schedule at sequence %d was expected at sequence %d", 0, s.Sequence))
			}
		} else if s.Sequence != last_sc.Sequence+1 {
			panic(fmt.Errorf("schedule at sequence %d was expected at sequence %d", last_sc.Sequence+1, s.Sequence))
		}

		if s.Route >= sizes["routes"] {
			panic(fmt.Errorf("schedule at sequence %d is referring to route at sequence %d which is out of range (length is %d)", s.Sequence, s.Route, len(d.routes)))
		}

		for _, ss := range s.ScheduleStops {
			if ss >= sizes["scheduleStops"] {
				panic(fmt.Errorf("schedule at sequence %d is referring to schedule stop at sequence %d which is out of range (length is %d)", s.Sequence, ss, sizes["scheduleStops"]))
			}
		}

		if bloomFilter.TestAndAddString(s.Id) {
			panic(fmt.Errorf("schedule at sequence %d has duplicated ID (%s)", s.Sequence, s.Id))
		}

		departAtSchedules[s.Sequence] = departAtScheduleStops[s.ScheduleStops[0]]

		last_sc = s
	}
	idsScheduleStops = nil // Free up memory
	if last_sc.Sequence != sizes["schedules"]-1 {
		panic(fmt.Errorf("Wrong schedules count %s, expected %s", last_sc.Sequence, sizes["schedules"]-1))
	}

	bloomFilter = bloom.NewWithEstimates(uint(sizes["stops"]), calculateBloomProbability(sizes["stops"]))
	var last_st *planner.Stop
	for s := range d.stops {
		if last_st == nil {
			if s.Sequence != 0 {
				panic(fmt.Errorf("stop at sequence %d was expected at sequence %d", 0, s.Sequence))
			}
		} else if s.Sequence != last_st.Sequence+1 {
			panic(fmt.Errorf("stop at sequence %d was expected at sequence %d", last_st.Sequence+1, s.Sequence))
		}

		for _, rs := range s.RouteStops {
			if rs >= sizes["routeStops"] {
				panic(fmt.Errorf("stop at sequence %d is referring to route stop at sequence %d which is out of range (length is %d)", s.Sequence, rs, sizes["routeStops"]))
			}
		}

		var lastDepartAt uint32
		for _, ss := range s.ScheduleStops {
			if ss >= sizes["scheduleStops"] {
				panic(fmt.Errorf("stop at sequence %d is referring to schedule stop at sequence %d which is out of range (length is %d)", s.Sequence, ss, sizes["scheduleStops"]))
			}

			departAt := departAtScheduleStops[ss]
			if ss > 0 && departAt < lastDepartAt {
				panic(fmt.Errorf("stop at sequence %d does not have its schedule stops sorted correctly", s.Sequence))
			}
			lastDepartAt = departAt
		}

		for _, t := range s.Transfers {
			if t >= sizes["transfers"] {
				panic(fmt.Errorf("stop at sequence %d is referring to transfer at sequence %d whichis out of range (length is %d)", s.Sequence, t, sizes["transfers"]))
			}
		}

		if bloomFilter.TestAndAddString(s.Id) {
			panic(fmt.Errorf("stop at sequence %d has duplicated ID (%s)", s.Sequence, s.Id))
		}
		last_st = s
	}
	departAtScheduleStops = nil // Free up memory
	if last_st.Sequence != sizes["stops"]-1 {
		panic(fmt.Errorf("Wrong stops count %s, expected %s", last_st.Sequence, sizes["stops"]-1))
	}

	var last_r *planner.Route
	for r := range d.routes {
		if last_r == nil {
			if r.Sequence != 0 {
				panic(fmt.Errorf("route at sequence %d was expected at sequence %d", 0, r.Sequence))
			}
		} else if r.Sequence != last_r.Sequence+1 {
			panic(fmt.Errorf("route at sequence %d was expected at sequence %d", last_r.Sequence+1, r.Sequence))
		}

		var lastDepartAt uint32
		for _, s := range r.Schedules {
			if s >= sizes["schedules"] {
				panic(fmt.Errorf("route at sequence %d is referring to schedule at sequence %d which is out of range (length is %d)", r.Sequence, s, sizes["schedules"]))
			}

			departAt := departAtSchedules[s]
			if s > 0 && departAt < lastDepartAt {
				panic(fmt.Errorf("route at sequence %d does not have its schedules sorted correctly", r.Sequence))
			}
			lastDepartAt = departAt
		}

		for _, rs := range r.RouteStops {
			if rs >= sizes["routeStops"] {
				panic(fmt.Errorf("route at sequence %d is referring to route stop at sequence %d which is out of range (length is %d)", r.Sequence, rs, sizes["routeStops"]))
			}
		}

		last_r = r
	}
	departAtSchedules = nil // Free up memory
	if last_r.Sequence != sizes["routes"]-1 {
		panic(fmt.Errorf("Wrong routes count %s, expected %s", last_r.Sequence, sizes["routes"]-1))
	}

	var last_rs *planner.RouteStop
	for rs := range d.routeStops {
		if last_rs == nil {
			if rs.Sequence != 0 {
				panic(fmt.Errorf("route stop at sequence %d was expected at sequence %d", 0, rs.Sequence))
			}
		} else if rs.Sequence != last_rs.Sequence+1 {
			panic(fmt.Errorf("route stop at sequence %d was expected at sequence %d", last_rs.Sequence+1, rs.Sequence))
		}

		if rs.Route >= sizes["routes"] {
			panic(fmt.Errorf("route stop at sequence %d is referring to route at sequence %d which is out of range (length is %d)", rs.Sequence, rs.Route, len(d.routes)))
		}

		if rs.Stop >= sizes["stops"] {
			panic(fmt.Errorf("route stop at sequence %d is referring to stop at sequence %d which is out of range (length is %d)", rs.Sequence, rs.Stop, sizes["stops"]))
		}
		last_rs = rs
	}
	if last_rs.Sequence != sizes["routeStops"]-1 {
		panic(fmt.Errorf("Wrong route_stops count %s, expected %s", last_rs.Sequence, sizes["routeStops"]-1))
	}

	var last_t *planner.Transfer
	for t := range d.transfers {
		if last_t == nil {
			if t.Sequence != 0 {
				panic(fmt.Errorf("transfer at sequence %d was expected at sequence %d", 0, t.Sequence))
			}
		} else if t.Sequence != last_t.Sequence+1 {
			panic(fmt.Errorf("transfer at sequence %d was expected at sequence %d", last_t.Sequence+1, t.Sequence))
		}

		if t.ToStop >= sizes["stops"] {
			panic(fmt.Errorf("transfer at sequence %d is referring to stop at sequence %d which is out of range (length is %d)", t.Sequence, t.ToStop, len(d.stops)))
		}

		if t.FromStop >= sizes["stops"] {
			panic(fmt.Errorf("transfer at sequence %d is referring to stop at sequence %d which is out of range (length is %d)", t.Sequence, t.FromStop, len(d.stops)))
		}
		last_t = t
	}
	if last_t.Sequence != sizes["transfers"]-1 {
		panic(fmt.Errorf("Wrong transfers count %s, expected %s", last_t.Sequence, sizes["transfers"]-1))
	}
}

func validateDataIntegrity(d dataset, sm map[string]schedule) []error {
	dataErrors := make([]error, 0)
	/*pSchedulesMap := make(map[string]*planner.Schedule, len(d.schedules))

	for _, ps := range d.schedules {
		pSchedulesMap[ps.Id] = ps
	}

	progressMessage := "Validating data integrity"
	bar := progressbar.Default(int64(len(sm)), fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
	percentCoverage := getCoverage() // env var VALIDATE_DATASET_COVERAGE
	var rowCount int

	for _, js := range sm {
		rowCount++
		if (rowCount % 100) >= percentCoverage {
			continue
		}

		check(bar.Add(1))

		ps, ok := pSchedulesMap[js.Id]

		legs := make([][2]*planner.ScheduleStop, 0, len(ps.ScheduleStops)-1)
		pScheduleId,  := uuid.Parse(ps.Id)

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
				dataErrors = append(dataErrors, fmt.Errorf("stop at sequence %d does not have a H3Index as ID (%s): %s", d.stops[legs[i][0].Stop].Sequence, d.stops[legs[i][0].Stop].Id, err))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			} else if uint64(originId) != uint64(originIndex) {
				dataErrors = append(dataErrors, fmt.Errorf("stop at sequence %d has an invalid ID (%d found, %d expected)", d.stops[legs[i][0].Stop].Sequence, originId, uint64(originIndex)))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			}

			if err2 != nil {
				dataErrors = append(dataErrors, fmt.Errorf("stop at sequence %d does not have a H3Index as ID (%s): %s", d.stops[legs[i][1].Stop].Sequence, d.stops[legs[i][1].Stop].Id, err2))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			} else if uint64(destinationId) != uint64(destinationIndex) {
				dataErrors = append(dataErrors, fmt.Errorf("stop at sequence %d has an invalid ID (%d found, %d expected)", d.stops[legs[i][1].Stop].Sequence, destinationId, uint64(destinationIndex)))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			}

			firstStopId, err := uuid.Parse(legs[i][0].Id)

			if err != nil {
				dataErrors = append(dataErrors, fmt.Errorf("schedule stop at sequence %d does not have a UUID as ID (%s): %s", legs[i][0].Sequence, legs[i][0].Id, err))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			}

			secondStopId, err2 := uuid.Parse(legs[i][1].Id)

			if err2 != nil {
				dataErrors = append(dataErrors, fmt.Errorf("schedule stop at sequence %d does not have a UUID as ID (%s): %s", legs[i][1].Sequence, legs[i][1].Id, err2))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			}

			if err == nil && err2 == nil {
				pLegId := uuid.NewSHA1(pScheduleId, []byte(
					strings.Join([]string{
						firstStopId.String(),
						secondStopId.String(),
					}, "\x00"),
				))

				if l.Id != pLegId.String() {
					dataErrors = append(dataErrors, fmt.Errorf("IDs for leg #%d in schedule %s do not match (%s in protobuf, %s in JSON)", i, pScheduleId.String(), l.Id, pLegId.String()))
					bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
				}
			}
		}

		jScheduleId, err := uuid.Parse(js.Id)

		if err != nil {
			dataErrors = append(dataErrors, fmt.Errorf("schedule in JSON does not have a UUID as ID (%s): %s", js.Id, err))
			bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
		} else {
			for i, l := range js.Legs {
				jLegId := uuid.NewSHA1(jScheduleId, []byte(
					strings.Join([]string{
						uuid.NewSHA1(jScheduleId, []byte(strconv.Itoa(i))).String(),
						uuid.NewSHA1(jScheduleId, []byte(strconv.Itoa(i+1))).String(),
					}, "\x00")))

				if l.Id != jLegId.String() {
					dataErrors = append(dataErrors, fmt.Errorf("ID for leg #%d in schedule %s has an invalid ID (%s found, %s expected)", i, jScheduleId.String(), l.Id, jLegId.String()))
					bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
				}
			}
		}

		if _, ok := models.Schedule_Type_name[int32(js.Type)]; !ok {
			dataErrors = append(dataErrors, fmt.Errorf("type for schedule %s is not a valid (%d)", js.Id, js.Type))
			bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
		}

		for i, l := range js.Legs {
			if js.Type != l.Type {
				dataErrors = append(dataErrors, fmt.Errorf("type for leg #%d in schedule %s does not match type of schedule (%d found, %d expected)", i, js.Id, l.Type, js.Type))
				bar.Describe(fmt.Sprintf("%s (%d dataErrors)", progressMessage, len(dataErrors)))
			}
		}
	}

	check(bar.Finish())*/

	return dataErrors
}

func getCoverage() int {
	// Read env var VALIDATE_DATASET_COVERAGE and return a value [1..100]
	// or 100 if no env var or is not a valid number
	percentStr, ok := os.LookupEnv("VALIDATE_DATASET_COVERAGE")
	if !ok {
		return 100
	}
	percent, err := strconv.Atoi(percentStr)
	if err != nil {
		log.Printf("WARNING enc var VALIDATE_DATASET_COVERAGE not an integer: %s (using 100%%): %v\n", percentStr, err)
		return 100
	}
	if percent < 1 || percent > 100 {
		log.Printf("enc var VALIDATE_DATASET_COVERAGE out of range [1..100] (using 100%%) : %d", percent)
		return 100
	}
	log.Printf("enc var VALIDATE_DATASET_COVERAGE is: %d%%", percent)
	return percent

}
