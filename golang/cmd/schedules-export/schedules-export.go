package main

/*
	Read the Schedules data from intermediate Protobuf BIN files (from gtfs-import)
	and create the .bin files containing raw Protobuf data.

	File locations are specified wit --input_dir and --output-dir.
*/
import (
	"bufio"
	"errors"
	"fmt"
	"hash/fnv"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"sync"

	plannerv1alpha "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/service/planner/v1alpha"
	v1alpha "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"
	"git.snowfall.se/junction/junction/golang/protoio"
	"github.com/google/uuid"
	"github.com/schollz/progressbar/v3"
	"github.com/uber/h3-go/v3"
	"google.golang.org/protobuf/types/known/timestamppb"
)

const (
	IsARouteStop StopSource = iota
	IsAScheduleStop
)

// Types

type StopSource uint8

type routesJob struct {
	schedule    *v1alpha.Schedule
	stops       []*v1alpha.Stop
	newSchedule uint64
	toRoute     uint64
}

type scheduleStopDataStruct struct {
	ScheduleStopId uint64
	startTime      int64
}
type stopJob struct {
	point                  *v1alpha.Point
	source                 StopSource
	parentScheduleStop     uint64
	parentSchedStopSeconds int64
	scheduleId             string
	departureTime          int64
}
type stopsWriterJob struct {
	cache             stopCache
	cacheSequenceList []uint64
}
type routesWriterJob struct {
	cache             routeCacheType
	cacheSequenceList []uint64
	departures        []uint32
	schedulesCache    schedulesCache
}
type schedulesWriterJob struct {
	cache             schedulesCache
	cacheSequenceList []uint64
}

type stopCache map[uint64]*stopCacheData

type stopCacheDataStop struct {
	stopId   uint64
	stopTime int64
}
type stopCacheData struct {
	stopId        uint64
	routeStops    []stopCacheDataStop
	scheduleStops []stopCacheDataStop
	scheduleId    string
	departureTime int64
}

func (cacheData *stopCacheData) addReferences(job *stopJob) {
	/*
		job.source is either RouteStop or ScheduleStop
		Add sequence to stopCacheData.routeStops or .scheduleStops
	*/
	stop := stopCacheDataStop{
		stopId:   job.parentScheduleStop,
		stopTime: job.departureTime,
	}

	switch job.source {
	case IsARouteStop:
		if len(cacheData.routeStops) > 0 && stop.stopId <= cacheData.routeStops[len(cacheData.routeStops)-1].stopId {
			panic("Unexepcted stopID.")
		}
		cacheData.routeStops = append(cacheData.routeStops, stop)
	case IsAScheduleStop:
		if len(cacheData.scheduleStops) > 0 && stop.stopId <= cacheData.scheduleStops[len(cacheData.scheduleStops)-1].stopId {
			panic(fmt.Sprintf("Unexepcted stopID (%d): %q.", stop.stopId, cacheData.scheduleStops))
		}
		cacheData.scheduleStops = append(cacheData.scheduleStops, stop)
	default:
		panic("Unexpected job.source: " + string(job.source))
	}
}

type schedulesCache map[uint64]*plannerv1alpha.Schedule

type boardingInfo struct {
	stopId           string
	BoardingAllowed  bool
	AlightingAllowed bool
}
type routeCacheType map[uint64]*plannerv1alpha.Route

type stopsExporterType struct {
	cache             stopCache
	sequence          uint64
	cacheSequenceList []uint64
}

func (self *stopsExporterType) add(job *stopJob) uint64 {
	identifier := getGeoIdentifier(job.point.Coordinates)

	if v, ok := self.cache[identifier]; ok {
		v.addReferences(job)
		return v.stopId
	}

	thisStop := stopCacheData{
		stopId:        self.sequence,
		routeStops:    nil,
		scheduleStops: nil,
		scheduleId:    job.scheduleId,
		departureTime: job.departureTime,
	}
	thisStop.addReferences(job)

	self.cache[identifier] = &thisStop
	self.cacheSequenceList = append(self.cacheSequenceList, identifier)
	self.sequence++
	return thisStop.stopId
}

/** Write out the current cache contents and reset. */
func (self *stopsExporterType) flush() {
	stopsChan <- &stopsWriterJob{
		cache:             self.cache,
		cacheSequenceList: self.cacheSequenceList,
	}
	self.cache = stopCache{}
	self.cacheSequenceList = make([]uint64, 0, 262144)
}

type routesExporterType struct {
	cache             routeCacheType
	sequence          uint64
	routeStopSequence uint64
	cacheSequenceList []uint64
	offset            uint64
	departures        []uint32
}

func (self *routesExporterType) addNewSchedule(job *routesJob) {
	index := job.toRoute - self.offset
	if index >= uint64(len(self.cacheSequenceList)) {
		panic(fmt.Errorf("adding schedule to non-existing route: %v", job.toRoute))
	}
	routeId := self.cacheSequenceList[index]
	thisRoute := self.cache[routeId]
	thisRoute.Schedules = append(thisRoute.Schedules, job.newSchedule)
}

func (self *routesExporterType) addDeparture(sequence uint64, d uint32) {
	if uint64(len(self.departures)) != sequence {
		panic("Incorrect sequence number.")
	}
	self.departures = append(self.departures, d)
}

func (self *routesExporterType) add(job *routesJob) uint64 {
	idBuilder := coordIdBuilder(job)
	identifier := idHash(idBuilder)

	if v, ok := self.cache[identifier]; ok {
		return v.Sequence
	}

	stops := make([]uint64, 0, len(job.stops))
	for index, stop := range job.stops {
		stopSequence := stopsExporter.add(&stopJob{
			point:                  stop.Point,
			source:                 IsARouteStop,
			parentScheduleStop:     self.routeStopSequence,
			parentSchedStopSeconds: getSafeDepartureTime(stop.DepartureAt),
			scheduleId:             job.schedule.Id,
			departureTime:          getSafeDepartureTime(stop.DepartureAt),
		})
		thisRouteStop := plannerv1alpha.RouteStop{
			Sequence: self.routeStopSequence,
			Route:    self.sequence,
			Stop:     stopSequence,
			Order:    uint32(index),
		}

		routeStopsChan <- &thisRouteStop

		self.routeStopSequence++
		stops = append(stops, thisRouteStop.Sequence)
	}

	// Not in cache, add new route
	thisRoute := &plannerv1alpha.Route{
		Sequence:   self.sequence,
		RouteStops: stops,
	}
	self.cache[identifier] = thisRoute
	self.cacheSequenceList = append(self.cacheSequenceList, identifier)
	self.sequence++
	return thisRoute.Sequence
}

/** Write out the current cache contents and reset. */
func (self *routesExporterType) flush() {
	routesChan <- &routesWriterJob{
		cache:             self.cache,
		cacheSequenceList: self.cacheSequenceList,
		departures:        self.departures,
		schedulesCache:    schedulesExporter.cache,
	}
	// Offset keeps track of where we need to index in the list with job.ToRoute.
	self.offset += uint64(len(self.cacheSequenceList))
	self.cache = routeCacheType{}
	self.cacheSequenceList = make([]uint64, 0, 262144)
}

type schedulesExporterType struct {
	cache             schedulesCache
	cacheSequenceList []uint64
	IdKey             map[string]bool
	count             uint64
}

func (self *schedulesExporterType) add(job *plannerv1alpha.Schedule) uint64 {
	if _, ok := self.IdKey[job.Id]; ok {
		// It's IN the cache - should not be called twice!
		panic(fmt.Errorf("schedule ID %v sequence %v received TWICE", job.Id, job.Sequence))
	}
	self.cache[job.Sequence] = job
	self.cacheSequenceList = append(self.cacheSequenceList, job.Sequence)
	self.count++
	self.IdKey[job.Id] = true
	routesExporter.addNewSchedule(&routesJob{
		newSchedule: job.Sequence,
		toRoute:     job.Route,
	})
	return job.Sequence
}

/** Write out the current cache contents and reset. */
func (self *schedulesExporterType) flush() {
	schedulesChan <- &schedulesWriterJob{
		cache:             self.cache,
		cacheSequenceList: self.cacheSequenceList,
	}
	self.cache = schedulesCache{}
	self.cacheSequenceList = make([]uint64, 0, 8192)
	self.IdKey = make(map[string]bool)
}

// Module vars
var stopsExporter = stopsExporterType{
	cache:             stopCache{},
	sequence:          0,
	cacheSequenceList: make([]uint64, 0, 262144),
}
var routesExporter = routesExporterType{
	cache:             routeCacheType{},
	sequence:          0,
	routeStopSequence: 0,
	cacheSequenceList: make([]uint64, 0, 262144),
	departures:        make([]uint32, 0, 262144),
}
var schedulesExporter = schedulesExporterType{
	cache:             schedulesCache{},
	cacheSequenceList: make([]uint64, 0, 8192),
	IdKey:             make(map[string]bool),
	count:             0,
}
var routesChan chan<- *routesWriterJob
var routeStopsChan chan<- *plannerv1alpha.RouteStop
var schedulesChan chan<- *schedulesWriterJob
var scheduleStopsChan chan<- *plannerv1alpha.ScheduleStop
var stopsChan chan<- *stopsWriterJob
var scheduleStopsSequence = uint64(0)

func idHash(idBuilder strings.Builder) uint64 {
	h := fnv.New64a()
	s := idBuilder.String()
	_, err := h.Write([]byte(s))
	check(err)
	return h.Sum64()
}

func coordIdBuilder(job *routesJob) strings.Builder {
	idBuilder := strings.Builder{}

	for _, stop := range job.stops {
		idBuilder.WriteString(
			strconv.FormatUint(uint64(h3.FromGeo(h3.GeoCoord{ // XXXXX Change here!
				Longitude: stop.Point.Coordinates.Longitude,
				Latitude:  stop.Point.Coordinates.Latitude,
			}, 9)), 10),
		)
	}
	return idBuilder
}

func routesWriterTask(writer io.Writer, wg *sync.WaitGroup) chan<- *routesWriterJob {
	ch := make(chan *routesWriterJob)

	go func() {
		defer wg.Done()

		w := bufio.NewWriter(writer)
		protoWriter := protoio.NewProtoWriter[*plannerv1alpha.Route](w)

		for job := range ch {
			if job == nil {
				break
			}

			for _, key := range job.cacheSequenceList {
				value := job.cache[key]

				sort.Slice(value.Schedules, func(i, j int) bool {
					return job.departures[job.schedulesCache[value.Schedules[i]].ScheduleStops[0]] <
						job.departures[job.schedulesCache[value.Schedules[j]].ScheduleStops[0]]
				})

				stopProto := plannerv1alpha.Route{
					Sequence:   value.Sequence,
					Schedules:  value.Schedules,
					RouteStops: value.RouteStops,
				}
				check(protoWriter.Write(&stopProto))
			}
		}
		check(w.Flush())
	}()

	return ch
}

func routeStopsWriterTask(writer io.Writer, wg *sync.WaitGroup) chan<- *plannerv1alpha.RouteStop {
	ch := make(chan *plannerv1alpha.RouteStop)

	go func() {
		defer wg.Done()
		w := bufio.NewWriter(writer)
		protoWriter := protoio.NewProtoWriter[*plannerv1alpha.RouteStop](w)

		for job := range ch {
			if job == nil {
				break
			}
			err := protoWriter.Write(job)
			if err != nil {
				panic(err)
			}
		}

		check(w.Flush())
	}()

	return ch
}

func schedulesWriterTask(writer io.Writer, wg *sync.WaitGroup) chan<- *schedulesWriterJob {
	ch := make(chan *schedulesWriterJob)

	go func() {
		defer wg.Done()
		w := bufio.NewWriter(writer)
		protoWriter := protoio.NewProtoWriter[*plannerv1alpha.Schedule](w)

		for job := range ch {
			if job == nil {
				break
			}

			sort.Slice(job.cacheSequenceList, func(i, j int) bool { return job.cacheSequenceList[i] < job.cacheSequenceList[j] })
			for _, key := range job.cacheSequenceList {
				check(protoWriter.Write(job.cache[key]))
			}
		}

		check(w.Flush())
	}()

	return ch
}

func scheduleStopsWriterTask(writer io.Writer, wg *sync.WaitGroup) chan<- *plannerv1alpha.ScheduleStop {
	ch := make(chan *plannerv1alpha.ScheduleStop)

	go func() {
		defer wg.Done()
		w := bufio.NewWriter(writer)
		protoWriter := protoio.NewProtoWriter[*plannerv1alpha.ScheduleStop](w)

		for job := range ch {
			if job == nil {
				break
			}

			routesExporter.addDeparture(job.Sequence, job.DepartureAt)

			err := protoWriter.Write(job)
			if err != nil {
				panic(err)
			}
		}

		check(w.Flush())
	}()

	return ch
}

func stopsWriterTask(writer io.Writer, wg *sync.WaitGroup) chan<- *stopsWriterJob {
	/*
		Creates and starts anonymous Go routine,
		that wakes and processes stopJob messages.
		Creates a new Stop on first use and caches it.
		Returns ID if already cached.
		Adds either scheduleID or routeID to cache on each call.
		Writes cache to BIN file when channel closed.
		There is only ONE of these running.
	*/
	ch := make(chan *stopsWriterJob) // becomes the global stopsChan

	go func() {
		defer wg.Done()

		w := bufio.NewWriter(writer)
		protoWriter := protoio.NewProtoWriter[*plannerv1alpha.Stop](w)

		for job := range ch {
			if job == nil {
				break
			}

			for _, key := range job.cacheSequenceList {
				value := job.cache[key]
				stopProto := plannerv1alpha.Stop{
					Sequence:      value.stopId,
					Id:            strconv.FormatUint(key, 10), // The cache key IS the H3 geoidentifier
					TransferTime:  0,
					RouteStops:    extractAndSortRouteStopIds(value.routeStops),
					ScheduleStops: extractAndSortRouteStopIds(value.scheduleStops),
					Transfers:     nil,
				}
				check(protoWriter.Write(&stopProto))
			}
		}
		check(w.Flush())
	}()

	return ch
}

func getSafeDepartureTime(departureAt *timestamppb.Timestamp) int64 {
	if departureAt != nil {
		return departureAt.Seconds
	} else {
		return 0
	}
}

func generateScheduleStopId(scheduleId string, stopIndex uint32) string {
	if len(scheduleId) == 0 {
		panic("Got a zero length ScheduleID")
	}
	schedUuid, err := uuid.Parse(scheduleId)
	check(err)
	id := uuid.NewSHA1(schedUuid, uint32ToByte(stopIndex))
	return id.String()
}

func extractAndSortRouteStopIds(stops []stopCacheDataStop) []uint64 {
	ids := make([]uint64, 0, len(stops))
	sort.Slice(stops, func(i, j int) bool {
		return stops[i].stopTime < stops[j].stopTime
	})
	for _, st := range stops {
		ids = append(ids, st.stopId)
	}
	return ids
}

func closeFile(f io.ReadCloser) {
	check(f.Close())
}

func generateStopsFromLegs(legs []*v1alpha.Leg) (*[]*v1alpha.Stop, *[]*boardingInfo) {
	stops := make([]*v1alpha.Stop, 0, len(legs)+1)
	onOffs := make([]*boardingInfo, 0, len(legs)+1)

	for i, leg := range legs {
		stop := v1alpha.Stop{
			Id:          leg.Origin.Ref,
			DepartureAt: leg.DepartureAt,
			ArrivalAt:   nil,
			Point:       leg.Origin,
			Order:       uint32(i + 1),
		}
		AlightingAllowed := false
		// For first stop, arrival is nil
		if i > 0 {
			// Previous leg arrives at this stop.
			stop.ArrivalAt = legs[i-1].ArrivalAt
			AlightingAllowed = legs[i-1].AlightingAllowed
		}
		stops = append(stops, &stop)
		onOffs = append(onOffs, &boardingInfo{
			stopId:           stop.Id,
			BoardingAllowed:  leg.BoardingAllowed,
			AlightingAllowed: AlightingAllowed,
		})
	}

	lastLeg := legs[len(legs)-1]

	lastStop := v1alpha.Stop{
		Id:          lastLeg.Destination.Ref,
		DepartureAt: nil,
		ArrivalAt:   lastLeg.ArrivalAt,
		Point:       lastLeg.Destination,
		Order:       uint32(len(legs) + 1),
	}
	stops = append(stops, &lastStop)
	onOffs = append(onOffs, &boardingInfo{
		stopId:           lastStop.Id,
		BoardingAllowed:  false,                    // Cannot get on at last stop!
		AlightingAllowed: lastLeg.AlightingAllowed, // Presumably always true?
	})
	return &stops, &onOffs
}

func buildScheduleStops(schedule *v1alpha.Schedule, sequence uint64) ([]uint64, []*v1alpha.Stop) {
	ScheduleStops := make([]scheduleStopDataStruct, 0, len(schedule.Stops))

	stops, boardingInfo := generateStopsFromLegs(schedule.Legs)
	for _, stop := range *stops {
		boarding := *(*boardingInfo)[stop.Order-1]

		scheduleStopsParentStop := stopsExporter.add(&stopJob{
			point:                  stop.Point,
			source:                 IsAScheduleStop,
			parentScheduleStop:     scheduleStopsSequence,
			parentSchedStopSeconds: getSafeDepartureTime(stop.DepartureAt),
			scheduleId:             schedule.Id,
			departureTime:          getSafeDepartureTime(stop.DepartureAt),
		}) // Will return an existing stop if coords in job.stop.Point
		// match an exiting stop to H3 precision 9

		schedStopId := generateScheduleStopId(schedule.Id, stop.Order-1)

		scheduleStopsChan <- &plannerv1alpha.ScheduleStop{
			Id:               schedStopId,
			Sequence:         scheduleStopsSequence,
			Schedule:         sequence,
			Stop:             scheduleStopsParentStop,
			DepartureAt:      maxU32(0, uint32(stop.DepartureAt.AsTime().Unix())),
			ArrivalAt:        maxU32(0, uint32(stop.ArrivalAt.AsTime().Unix())),
			Order:            uint32(stop.Order - 1),
			BoardingAllowed:  boarding.BoardingAllowed,
			AlightingAllowed: boarding.AlightingAllowed,
		}

		scheduleStopData := scheduleStopDataStruct{
			ScheduleStopId: scheduleStopsSequence,
			startTime:      getSafeDepartureTime(stop.DepartureAt),
		}
		ScheduleStops = append(ScheduleStops, scheduleStopData)
		scheduleStopsSequence++
	}
	return getSortedScheduleStops(ScheduleStops), *stops
}

func getSortedScheduleStops(scheduleStops []scheduleStopDataStruct) []uint64 {
	// sort.Slice(scheduleStops, func(i, j int) bool {
	// 	return scheduleStops[i].startTime < scheduleStops[j].startTime
	// })
	result := make([]uint64, 0, len(scheduleStops))

	for _, v := range scheduleStops {
		result = append(result, v.ScheduleStopId)
	}
	return result
}

func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())

	fmt.Println("\n\nschedules-export STARTING")
	var fileWriterWg sync.WaitGroup

	env := getParams()

	f, err := os.OpenFile(filepath.Join(env.outputPath, "routes.bin"), os.O_CREATE|os.O_WRONLY, 0644)
	check(err)
	defer closeFile(f)
	fileWriterWg.Add(1)
	routesChan = routesWriterTask(f, &fileWriterWg)

	f, err = os.OpenFile(filepath.Join(env.outputPath, "route_stops.bin"), os.O_CREATE|os.O_WRONLY, 0644)
	check(err)
	defer closeFile(f)
	fileWriterWg.Add(1)
	routeStopsChan = routeStopsWriterTask(f, &fileWriterWg)

	f, err = os.OpenFile(filepath.Join(env.outputPath, "schedules.bin"), os.O_CREATE|os.O_WRONLY, 0644)
	check(err)
	defer closeFile(f)
	fileWriterWg.Add(1)
	schedulesChan = schedulesWriterTask(f, &fileWriterWg)

	f, err = os.OpenFile(filepath.Join(env.outputPath, "schedule_stops.bin"), os.O_CREATE|os.O_WRONLY, 0644)
	check(err)
	defer closeFile(f)
	fileWriterWg.Add(1)
	scheduleStopsChan = scheduleStopsWriterTask(f, &fileWriterWg)

	f, err = os.OpenFile(filepath.Join(env.outputPath, "stops.bin"), os.O_CREATE|os.O_WRONLY, 0644)
	check(err)
	defer closeFile(f)
	fileWriterWg.Add(1)
	stopsChan = stopsWriterTask(f, &fileWriterWg)

	// Create an empty transfers.bin
	f, err = os.OpenFile(filepath.Join(env.outputPath, "transfers.bin"), os.O_CREATE|os.O_WRONLY, 0644)
	check(err)
	closeFile(f)

	// Now open the main Input file
	f, err = os.OpenFile(filepath.Join(env.dataPath, "/schedules.bin"), os.O_RDONLY, 0644)
	check(err)
	defer closeFile(f)
	stat, err := f.Stat()
	check(err)
	fmt.Println("All input files open, output files created")

	bar := progressbar.DefaultBytes(stat.Size(), "Exporting")

	barReader := progressbar.NewReader(f, bar)
	protoReader := protoio.NewProtoReader[*v1alpha.Schedule](bufio.NewReader(&barReader))

	sequence := uint64(0)
	lastSource := ""
	for {
		// Read the input intermediate Schedules protobuf file
		var msg v1alpha.Schedule

		err = protoReader.ReadNext(&msg) // Each Intermediate Schedules protobuf doc
		if err == io.EOF {
			break
		}
		if errors.Is(err, io.ErrUnexpectedEOF) {
			panic(">>>>> Unexpected EOF - possibly corrupt BIN file ")
		}
		check(err)

		// Flush cached data after each input file has completed processing.
		if msg.SourceRef != lastSource {
			if lastSource != "" {
				// Stops are referenced between source files, so can't be flushed.
				// stopsExporter.flush()
				routesExporter.flush()
				schedulesExporter.flush()
			}
			lastSource = msg.SourceRef
		}

		ScheduleStopIds, stops := buildScheduleStops(&msg, sequence)
		if len(ScheduleStopIds) > 0 {
			routeSequence := routesExporter.add(&routesJob{
				schedule:    &msg,
				stops:       stops,
				newSchedule: sequence,
			})

			schedulesExporter.add(&plannerv1alpha.Schedule{
				Sequence:      sequence,
				Id:            msg.Id,
				Type:          msg.Type,
				Route:         routeSequence,
				ScheduleStops: ScheduleStopIds,
			})
		}

		sequence++
	}

	stopsExporter.flush()
	routesExporter.flush()
	schedulesExporter.flush()

	// Inform the workers to finish.
	scheduleStopsChan <- nil
	schedulesChan <- nil
	routeStopsChan <- nil
	routesChan <- nil
	stopsChan <- nil

	fileWriterWg.Wait()
	close(stopsChan)
	close(routesChan)
	close(routeStopsChan)
	close(schedulesChan)
	close(scheduleStopsChan)

	// Store total number of records in each file to aid validate step.
	f, err = os.Create(filepath.Join(env.outputPath, "_sizes"))
	check(err)
	_, err = fmt.Fprintf(
		f, "scheduleStops %d\nschedules %d\nrouteStops %d\nroutes %d\nstops %d\ntransfers %d",
		scheduleStopsSequence, schedulesExporter.count, routesExporter.routeStopSequence,
		routesExporter.sequence, stopsExporter.sequence, 0,
	)
	check(err)
	closeFile(f)
}
