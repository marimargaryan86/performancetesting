package main

/*
Given a directory of many GTFS ZIP files, extracts each and uses the many .TXT files
to create two DB-format (using BSON) and two BIN files for Locations and schedules.
The BIN files are used by cmd/schedules-export/schedules-export.go to create
the final BIN files, used in turn by Planner
The DB-format files are used to load the MongoDB collections.

Requires command line parameters for:
	1) Path to the ZIP files
	2) Directory for the output files
	3) (Optional) number of days into the future to include data
		(helpful to create smaller test datasets).

Creates a temporary directory for the .TXT files, destroyed on exit
*/

import (
	"archive/zip"
	"bufio"
	_ "embed"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"reflect"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"git.snowfall.se/junction/junction/golang/gtfs"
	v1alphaLocations "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/service/places/v1alpha"
	v1alpha "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"
	"git.snowfall.se/junction/junction/golang/protoio"
	"github.com/bits-and-blooms/bloom"
	"github.com/catmullet/tz"
	"github.com/google/uuid"
	"github.com/schollz/progressbar/v3"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/bsoncodec"
	"go.mongodb.org/mongo-driver/bson/bsontype"
	"google.golang.org/protobuf/types/known/timestamppb"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

const namespace = "3cbbd269-773c-481b-bc1c-c59dfc19a063"

/*
 ******** Type Defs
	These are the structs to define the Json output for MongoDB input
	Based on but significantly different to type Schedule and Locations (Places)
	See protobuf/snowfall/stdlib/v1alpha/models.pb.go
*/

type mongoCoordinate struct {
	CoordType   string    `json:"type"`        // Always "Point"
	Coordinates []float64 `json:"coordinates"` // Lat, Lon
}

type mongoNode struct { // origin and destination objects in Schedule, for MongoDB
	Ref      string          `json:"ref"`
	Name     string          `json:"name"`
	Coord    mongoCoordinate `json:"coordinates"`
	TimeZone string          `json:"time_zone"`
}

type ConvertibleTime timestamppb.Timestamp

// For an interface function, below

type mongoLeg struct {
	Id               string                `json:"_id"`
	Origin           mongoNode             `json:"origin"`
	Destination      mongoNode             `json:"destination"`
	DepartureAt      *ConvertibleTime      `json:"departure_at"`
	ArrivalAt        *ConvertibleTime      `json:"arrival_at"`
	Type             v1alpha.Schedule_Type `json:"type"`
	AgencyName       string                `json:"agency_name"`
	BoardingAllowed  bool                  `json:"boarding_allowed"`
	AlightingAllowed bool                  `json:"alighting_allowed"`
}

type mongoSchedule struct {
	// json (for MongoDB load) match to *v1alpha.Schedule
	Id         string                `json:"_id"`
	Name       string                `json:"name"`
	AgencyName string                `json:"agency_name"`
	UpdatedAt  *ConvertibleTime      `json:"updated_at"`
	SourceRef  string                `json:"source_ref"`
	Type       v1alpha.Schedule_Type `json:"type"`
	Legs       []mongoLeg            `json:"legs"`
}

type mongoLocation struct {
	// json (for MongoDB load) match to *v1alphaLocations.Locations
	Id          string                           `json:"_id"`
	Name        string                           `json:"name"`
	Coordinates mongoCoordinate                  `json:"coordinates"`
	TimeZone    string                           `json:"time_zone"`
	UpdatedAt   *ConvertibleTime                 `json:"updated_at"`
	SourceRef   string                           `json:"source_ref"`
	Types       []v1alphaLocations.Location_Type `json:"types"`
}

var bsonRegistry *bsoncodec.Registry

//go:embed datasets.json
var datasetsFile []byte

//go:embed routes-whitelist.json
var routesWhitelistFile []byte

// ******** Interface functions

func (t *ConvertibleTime) MarshalBSONValue() (bsontype.Type, []byte, error) {
	// Convert a Google timestamppb.Timestamp protobuf time to a BSON DateTime.
	return bson.MarshalValueWithRegistry(bsonRegistry, time.Unix(t.Seconds, int64(t.Nanos)).UTC())
}

// ******** Functions

func newMongoPointCoords(point *v1alpha.Point) *mongoCoordinate {
	if point.Coordinates.Latitude > 90 || point.Coordinates.Latitude < -90 ||
		point.Coordinates.Longitude > 180 || point.Coordinates.Longitude < -180 {
		panic(fmt.Sprintf("Cordinates out of range: %v", point.Coordinates))
	}
	return &mongoCoordinate{
		CoordType:   "Point",
		Coordinates: []float64{point.Coordinates.Longitude, point.Coordinates.Latitude},
	}
}

func newMongoNode(node *v1alpha.Point) *mongoNode {
	return &mongoNode{
		Ref:      node.Ref,
		Name:     node.Name,
		Coord:    *newMongoPointCoords(node),
		TimeZone: node.TimeZone,
	}
}

func newMongoLeg(leg *v1alpha.Leg) *mongoLeg {
	// Note, some times are nil !!
	var depAt, arrAt *ConvertibleTime

	if leg.DepartureAt == nil {
		depAt = &ConvertibleTime{Seconds: 0}
	} else {
		depAt = &ConvertibleTime{Seconds: leg.DepartureAt.Seconds}
	}

	if leg.ArrivalAt == nil {
		arrAt = &ConvertibleTime{Seconds: 0}
	} else {
		arrAt = &ConvertibleTime{Seconds: leg.ArrivalAt.Seconds}
	}

	return &mongoLeg{
		Id:               leg.Id,
		Origin:           *newMongoNode(leg.Origin),
		Destination:      *newMongoNode(leg.Destination),
		DepartureAt:      depAt,
		ArrivalAt:        arrAt,
		Type:             leg.Type,
		AgencyName:       leg.AgencyName,
		BoardingAllowed:  leg.BoardingAllowed,
		AlightingAllowed: leg.AlightingAllowed,
	}
}

func newMongoSchedule(sched *v1alpha.Schedule) *mongoSchedule {
	legs := make([]mongoLeg, 0, len(sched.Legs))
	for _, leg := range sched.Legs {
		legs = append(legs, *newMongoLeg(leg))
	}

	return &mongoSchedule{
		Id:         sched.Id,
		Name:       sched.Name,
		AgencyName: sched.AgencyName,
		UpdatedAt:  &ConvertibleTime{Seconds: int64(time.Now().Unix())},
		SourceRef:  sched.SourceRef,
		Type:       sched.Type,
		Legs:       legs,
	}
}

func newMongoLocation(locationBuff *v1alphaLocations.Location, now time.Time) *mongoLocation {
	return &mongoLocation{
		Id:   locationBuff.Id,
		Name: locationBuff.Name,
		Coordinates: mongoCoordinate{
			CoordType: "Point",
			Coordinates: []float64{locationBuff.Coordinates.Longitude,
				locationBuff.Coordinates.Latitude},
		},
		TimeZone:  locationBuff.TimeZone,
		UpdatedAt: &ConvertibleTime{Seconds: int64(now.Unix())},
		SourceRef: locationBuff.SourceRef,
		Types:     locationBuff.Types,
	}
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func closeFile(f io.Closer) {
	check(f.Close())
}

var serviceDateCache map[string][]time.Time

func serviceDates(serviceId string, calendarDates []*gtfs.CalendarDate, calendars []*gtfs.Calendar, timeZone *time.Location, cutoff time.Time) []time.Time {
	if v, ok := serviceDateCache[serviceId]; ok {
		return v
	}

	now := time.Now()
	// No point including today's data, as it won't be relevant by the time it's deployed.
	now = now.AddDate(0, 0, 1)
	now = time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, timeZone)
	result := make(map[time.Time]struct{}, 0)

	for _, calendar := range calendars {
		weekdays := [7]bool{calendar.Sunday, calendar.Monday, calendar.Tuesday, calendar.Wednesday, calendar.Thursday, calendar.Friday, calendar.Saturday}
		anyOk := false

		for _, weekday := range weekdays {
			if weekday {
				anyOk = true
				break
			}
		}

		if !anyOk {
			continue
		}

		diff := (int(calendar.EndDate.Sub(calendar.StartDate).Hours()) / 24) + 1

		for i := 0; i < diff; i++ {
			current := calendar.StartDate.AddDate(0, 0, i)
			current = time.Date(
				current.Year(),
				current.Month(),
				current.Day(),
				0,
				0,
				0,
				0,
				timeZone,
			)

			if current.Before(now) || !weekdays[current.Weekday()] || current.After(cutoff) {
				continue
			}

			result[current] = struct{}{}
		}
	}

	for _, calendarDate := range calendarDates {
		current := time.Date(
			calendarDate.Date.Year(),
			calendarDate.Date.Month(),
			calendarDate.Date.Day(),
			0,
			0,
			0,
			0,
			timeZone,
		)

		if calendarDate.ExceptionType == gtfs.Removed {
			delete(result, current)
		} else if calendarDate.ExceptionType == gtfs.Added {
			result[current] = struct{}{}
		}
	}

	actualDates := make([]time.Time, 0, len(result))

	for date := range result {
		actualDates = append(actualDates, date)
	}

	serviceDateCache[serviceId] = actualDates

	sort.SliceStable(actualDates, func(i, j int) bool {
		return actualDates[i].Before(actualDates[j])
	})

	return actualDates
}

func indexFile[T gtfs.FileType](file *zip.File, db *gorm.DB, callback func(T), filter func(T) bool) {
	/*
		Called for each of the .TXT files expanded from the GTFS.ZIP file.
		processes row by row:
			skipped if filter returns false,
			else calls func callback to process it.
			Adds the rows to the (SQLite) DB (in batches)
		NB tried to run in parallel go routines, batch-update locks the DB
		and so causes a failure when 2 batches complete at the same time.
	*/
	var row T

	check(db.AutoMigrate(&row))

	f, err := file.Open()
	check(err)

	i := 0
	batch := make([]T, 0, db.CreateBatchSize)
	closer := io.ReadCloser(f)

	br := bufio.NewReader(closer)
	discardEncodingKeyword(br)

	fileReader, err := gtfs.NewReader[T](br)
	check(err)

	for {
		if i != 0 && i%db.CreateBatchSize == 0 {
			db.Create(&batch)
			batch = make([]T, 0, db.CreateBatchSize)
		}

		row, err = fileReader.Next()
		if err == io.EOF {
			break
		}
		check(err)

		if !filter(row) {
			continue
		}
		if callback != nil {
			callback(row)
		}

		batch = append(batch, row)
		i++
	}

	if len(batch) > 0 {
		db.Create(&batch)
	}
}

func discardEncodingKeyword(br *bufio.Reader) {
	next, _, err := br.ReadRune()
	check(err)

	if next != '\uFEFF' {
		check(br.UnreadRune())
	}
}

func getScheduleProtoWriter(schedulesBinFile *os.File, wg *sync.WaitGroup) chan *v1alpha.Schedule {
	bufScheduleWriter := bufio.NewWriter(schedulesBinFile)
	writer := protoio.NewProtoWriter(bufScheduleWriter)
	scheduleProtoChannel := make(chan *v1alpha.Schedule)

	go func() {
		defer wg.Done()

		for proto := range scheduleProtoChannel {
			if proto == nil {
				break
			}
			check(writer.Write(proto))
		}

		check(bufScheduleWriter.Flush())
	}()

	return scheduleProtoChannel
}

func GetWriteScheduleObj(schedFile *os.File, wg *sync.WaitGroup) chan *v1alpha.Schedule {
	schedFileWriter := bufio.NewWriter(schedFile)
	schedulesChannel := make(chan *v1alpha.Schedule)

	go func() {
		defer wg.Done()

		for schedBuff := range schedulesChannel {
			if schedBuff == nil {
				break
			}

			obj, err := bson.MarshalWithRegistry(bsonRegistry, newMongoSchedule(schedBuff))
			check(err)

			if _, err := schedFileWriter.Write(obj); err != nil {
				panic(fmt.Sprintf("GetWriteSchedule: Error writing\n: %v", err))
			}
		}

		check(schedFileWriter.Flush())
	}()

	return schedulesChannel
}

func writeLocationObj(schedulesObjFile *os.File, locationBuff *v1alphaLocations.Location, t time.Time) error {
	for i := range locationBuff.Types {
		if int(i) > 2 {
			panic(fmt.Sprintf("ERROR: bad key: %d\n", int(i)))
		}
	}
	obj, err := bson.MarshalWithRegistry(bsonRegistry, newMongoLocation(locationBuff, t))
	check(err)
	_, err = schedulesObjFile.Write(obj)
	return err
}

func destinationId(destination *gtfs.Stop, stopTz map[string]string) *v1alpha.Point {
	return &v1alpha.Point{
		Ref:  destination.Id,
		Name: destination.Name,
		Coordinates: &v1alpha.Coordinates{
			Latitude:  destination.Latitude,
			Longitude: destination.Longitude,
		},
		TimeZone: stopTz[destination.Id],
	}
}

func originId(origin *gtfs.Stop, stopTz map[string]string) *v1alpha.Point {
	return &v1alpha.Point{
		Ref:  origin.Id,
		Name: origin.Name,
		Coordinates: &v1alpha.Coordinates{
			Latitude:  origin.Latitude,
			Longitude: origin.Longitude,
		},
		TimeZone: stopTz[origin.Id],
	}
}

func generateLegId(scheduleId uuid.UUID, j int) string {
	return uuid.NewSHA1(scheduleId, []byte(strings.Join([]string{
		uuid.NewSHA1(scheduleId, []byte(strconv.Itoa(j))).String(), // StopID
		uuid.NewSHA1(scheduleId, []byte(strconv.Itoa(j+1))).String(),
	}, "\x00"))).String()
}

func processStopsTimesFile(files map[string]*zip.File, db *gorm.DB, stopTimesFilter *bloom.BloomFilter) {
	indexFile[gtfs.Stop](files["stops.txt"], db, nil, func(row gtfs.Stop) bool { // filter
		return stopTimesFilter.TestString(row.Id)
	})
}

func processStopTimeFile(files map[string]*zip.File, db *gorm.DB, stopTimesFilter *bloom.BloomFilter, tripsFilter *bloom.BloomFilter) {
	indexFile[gtfs.StopTime](
		files["stop_times.txt"], db,
		func(row gtfs.StopTime) { // callback
			stopTimesFilter.AddString(row.StopId)
		},
		func(row gtfs.StopTime) bool { // filter
			return tripsFilter.TestString(row.TripId) && (row.DropOffType == 0 || row.PickupType == 0)
		},
	)
}

func processTripFile(files map[string]*zip.File, db *gorm.DB, tripsFilter *bloom.BloomFilter,
	routesFilter *bloom.BloomFilter, servicesFilter *bloom.BloomFilter) {
	indexFile[gtfs.Trip](
		files["trips.txt"], db,
		func(row gtfs.Trip) { // callback
			tripsFilter.AddString(row.Id)
		},
		func(row gtfs.Trip) bool { // filter
			if !routesFilter.TestString(row.RouteId) {
				return false
			}

			return servicesFilter.TestString(row.ServiceId)
		})
}

func processRoutes(files map[string]*zip.File, db *gorm.DB, routesFilter *bloom.BloomFilter, validRouteTypes map[v1alpha.Schedule_Type]struct{}) {
	indexFile[gtfs.Route](
		files["routes.txt"], db,
		func(row gtfs.Route) {
			routesFilter.AddString(row.Id)
		},
		func(row gtfs.Route) bool { // filter
			_, ok := validRouteTypes[gtfsTypeMapping[row.Type]]
			return ok
		})
}

func processCalendarDatesFile(files map[string]*zip.File, db *gorm.DB, servicesFilter *bloom.BloomFilter, now time.Time) {
	if _, ok := files["calendar_dates.txt"]; ok {
		indexFile[gtfs.CalendarDate](
			files["calendar_dates.txt"], db,
			func(row gtfs.CalendarDate) {
				servicesFilter.AddString(row.ServiceId)
			},
			func(row gtfs.CalendarDate) bool {
				return now.Before(row.Date)
			})
	}
}

func processCalendarFile(files map[string]*zip.File, db *gorm.DB, servicesFilter *bloom.BloomFilter, now time.Time) {
	if _, ok := files["calendar.txt"]; ok {
		indexFile[gtfs.Calendar](
			files["calendar.txt"], db,
			func(row gtfs.Calendar) {
				servicesFilter.AddString(row.ServiceId)
			},
			func(row gtfs.Calendar) bool {
				return now.Before(row.EndDate)
			})
	}
}

func getFileMap(zf *zip.ReadCloser) map[string]*zip.File {
	// return a map of all file basename -> file path
	files := make(map[string]*zip.File, len(zf.File))

	for _, file := range zf.File {
		files[filepath.Base(file.Name)] = file
	}
	return files
}

// ******** MAIN

type locationTypesMap map[v1alphaLocations.Location_Type]bool

func main() {
	// JSONFallback will cause BSON to be generated with the correct tags.
	structcodec, err := bsoncodec.NewStructCodec(bsoncodec.JSONFallbackStructTagParser)
	check(err)
	rb := bson.NewRegistryBuilder()
	rb.RegisterDefaultEncoder(reflect.Struct, structcodec)
	rb.RegisterDefaultDecoder(reflect.Struct, structcodec)
	bsonRegistry = rb.Build()

	lookup, err := tz.NewTZ()
	check(err)

	inputDir := os.Args[1]
	check(os.MkdirAll(inputDir, 0755))
	outputDir := os.Args[2]
	check(os.MkdirAll(outputDir, 0755))
	now := time.Now()
	now = time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, time.UTC)
	cutoffDate := now.AddDate(2, 0, 0) // 2 years by default.
	if len(os.Args) >= 4 {
		days, err := strconv.Atoi(os.Args[3])
		check(err)
		cutoffDate = now.AddDate(0, 0, days)
	}
	programStartTime := time.Now()

	var fileWriterWg sync.WaitGroup

	file, err := os.Create(filepath.Join(outputDir, "schedules.bson"))
	check(err)
	defer closeFile(file)
	fileWriterWg.Add(1)
	scheduleObjWriterChan := GetWriteScheduleObj(file, &fileWriterWg)

	file, err = os.Create(filepath.Join(outputDir, "schedules.bin"))
	check(err)
	defer closeFile(file)
	fileWriterWg.Add(1)
	scheduleProtoWriterChan := getScheduleProtoWriter(file, &fileWriterWg)

	locationsObjFile, err := os.Create(filepath.Join(outputDir, "locations.bson"))
	check(err)
	defer closeFile(locationsObjFile)

	locationBinFile, err := os.Create(filepath.Join(outputDir, "locations.bin"))
	check(err)
	defer closeFile(locationBinFile)
	bufLocationWriter := bufio.NewWriter(locationBinFile)
	locationWriter := protoio.NewProtoWriter(bufLocationWriter)

	feedFiles, err := os.ReadDir(inputDir)
	check(err)
	totalFiles := len(feedFiles)
	if totalFiles < 1 {
		panic("ERROR No .ZIP files found in file source.")
	}

	var routesWhitelist map[string][]string
	if err := json.Unmarshal(routesWhitelistFile, &routesWhitelist); err != nil {
		panic(err)
	}

	for fileCount, feedFileName := range feedFiles {
		if filepath.Ext(feedFileName.Name()) != ".zip" {
			// Skip annoying local files like .DS_Store
			log.Printf("\nSKIP: %v (%d of %d)\n", feedFileName.Name(), fileCount+1, totalFiles)
			continue
		}

		func() {
			log.Printf("\nProcessing: %v (%d of %d)\n", feedFileName.Name(), fileCount+1, totalFiles)

			serviceDateCache = make(map[string][]time.Time)

			re := regexp.MustCompile(`-\d+\.zip$`) // Dedupe files from same provider.
			sourceRef := re.ReplaceAllLiteralString(feedFileName.Name(), ".zip")
			sourceRef = strings.TrimSuffix(sourceRef, ".zip")

			fileNamespace := uuid.NewSHA1(uuid.MustParse(namespace), []byte(sourceRef))
			fName := inputDir + "/" + feedFileName.Name()
			zf, err := zip.OpenReader(fName)
			check(err)
			defer zf.Close()

			files := getFileMap(zf)

			if _, ok := files["stop_times.txt"]; !ok {
				return
			}

			fmt.Println("--- " + sourceRef + " ---")

			tempFile, err := os.CreateTemp("", "gtfs-import")
			check(err)
			check(tempFile.Close())
			defer os.Remove(tempFile.Name())

			db, err := gorm.Open(sqlite.Open(tempFile.Name()), &gorm.Config{CreateBatchSize: 1000, SkipDefaultTransaction: true, PrepareStmt: false})
			check(err)

			db.Exec("PRAGMA journal_mode = off")
			db.Exec("PRAGMA synchronous = off")
			db.Exec("PRAGMA locking_mode = EXCLUSIVE")
			db.Exec("PRAGMA temp_store = MEMORY")

			routesFilter := bloom.NewWithEstimates(1000000, 0.001)
			tripsFilter := bloom.NewWithEstimates(1000000, 0.001)
			servicesFilter := bloom.NewWithEstimates(1000000, 0.001)
			stopTimesFilter := bloom.NewWithEstimates(1000000, 0.001)
			validRouteTypes := make(map[v1alpha.Schedule_Type]struct{})
			fileStem := strings.TrimSuffix(feedFileName.Name(), filepath.Ext(feedFileName.Name()))
			whitelist, ok := routesWhitelist[fileStem]
			if !ok {
				// Match partial names (e.g. ssim-ba match ssim, OBB-1 match OBB).
				prefix, _, _ := strings.Cut(fileStem, "-")
				whitelist, ok = routesWhitelist[prefix]
				if !ok {
					panic(fmt.Sprintf("No whitelist found for %s", fileStem))
				}
			}
			for _, typeName := range whitelist {
				t, ok := whitelistTypeMapping[typeName]
				if !ok {
					panic(fmt.Sprintf("Unrecognised type in whitelist: %s", typeName))
				}
				validRouteTypes[t] = struct{}{}
			}

			now := time.Now()
			now = time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())

			processRoutes(files, db, routesFilter, validRouteTypes)
			processCalendarFile(files, db, servicesFilter, now)
			processCalendarDatesFile(files, db, servicesFilter, now)
			processTripFile(files, db, tripsFilter, routesFilter, servicesFilter)
			processStopTimeFile(files, db, stopTimesFilter, tripsFilter)
			processStopsTimesFile(files, db, stopTimesFilter)
			agencyFile, err := files["agency.txt"].Open()
			check(err)

			progress := progressbar.NewReader(agencyFile, progressbar.DefaultBytes(
				files["agency.txt"].FileInfo().Size(),
				"Generating schedules",
			))

			closer := io.ReadCloser(&progress)
			defer closeFile(closer)

			br := bufio.NewReader(closer)
			discardEncodingKeyword(br)

			fileReader, err := gtfs.NewReader[gtfs.Agency](br)
			check(err)

			stopTypes := make(map[string]locationTypesMap)

			for { // Each Agency
				agency, err := fileReader.Next()
				if err == io.EOF {
					break
				}
				check(err)

				routes := make([]*gtfs.Route, 0)
				db.Where("agency_id = ?", agency.Id).Order("id ASC").Find(&routes)

				// ssim agencies should have routes, gtfs agencies may not.
				if strings.HasPrefix(feedFileName.Name(), "ssim") && len(routes) == 0 {
					panic(fmt.Sprintf("Agency: %s, no routes!", agency.Name))
				}
				for _, route := range routes {
					routeName := route.ShortName
					routeType := gtfsTypeMapping[route.Type]

					if routeName == "" {
						routeName = route.LongName
					}

					trips := make([]*gtfs.Trip, 0)

					db.Where("route_id = ?", route.Id).Order("id ASC").Find(&trips)

					for _, trip := range trips {
						stopTimes := make([]*gtfs.StopTime, 0)

						db.Where("trip_id = ?", trip.Id).Order("stop_sequence ASC").Find(&stopTimes)

						tripStops := make(map[string]*gtfs.Stop, len(stopTimes))
						stopTz := make(map[string]string, len(stopTimes))

						for _, stopTime := range stopTimes {
							var stop *gtfs.Stop
							db.Where("id = ?", stopTime.StopId).First(&stop)

							tripStops[stop.Id] = stop
							stopTz[stop.Id] = lookup.TimeZone(stop.Latitude, stop.Longitude)
							typ := scheduleTypeMapping[routeType]
							newStopTypeMap, ok := stopTypes[stop.Id]
							if !ok {
								newStopTypeMap = make(locationTypesMap)
							}
							newStopTypeMap[typ] = true
							stopTypes[stop.Id] = newStopTypeMap
						}

						calendarDates := make([]*gtfs.CalendarDate, 0)
						if _, ok := files["calendar_dates.txt"]; ok {
							db.Where("service_id = ?", trip.ServiceId).Find(&calendarDates)
						}

						calendars := make([]*gtfs.Calendar, 0)
						if _, ok := files["calendar.txt"]; ok {
							db.Where("service_id = ?", trip.ServiceId).Find(&calendars)
						}

						for _, serviceDate := range serviceDates(trip.ServiceId, calendarDates, calendars, agency.Timezone, cutoffDate) {
							legs := make([]*v1alpha.Leg, 0, len(stopTimes))
							scheduleId := uuid.NewSHA1(fileNamespace, []byte(strings.Join([]string{
								trip.Id,
								serviceDate.Format("2006-01-02"),
							}, "\x00")))

							for j := 0; j+1 < len(stopTimes); j++ {
								/* pickup_type and drop_off_type for TRAINS
								0 or empty - Regularly scheduled pickup.
								1 No pickup available.
								2 - Must phone agency to arrange pickup.
								3 - Must coordinate with driver to arrange pickup
								https://developers.google.com/transit/gtfs/reference
								for PLANES is a bit different
								*/

								BoardingAllowed, AlightingAllowed := getOnOff(agency, stopTimes, j)

								legs = append(legs, &v1alpha.Leg{
									Id:               generateLegId(scheduleId, j),
									Origin:           originId(tripStops[stopTimes[j].StopId], stopTz),
									Destination:      destinationId(tripStops[stopTimes[j+1].StopId], stopTz),
									DepartureAt:      timestamppb.New(serviceDate.Add(stopTimes[j].DepartureTime)),
									ArrivalAt:        timestamppb.New(serviceDate.Add(stopTimes[j+1].ArrivalTime)),
									Type:             gtfsTypeMapping[route.Type],
									AgencyName:       agency.Name,
									BoardingAllowed:  BoardingAllowed,
									AlightingAllowed: AlightingAllowed,
								})
							}

							if len(legs) < 1 {
								break
							}

							newSchedule := v1alpha.Schedule{
								Id:         scheduleId.String(),
								Name:       routeName,
								AgencyName: agency.Name,
								SourceRef:  sourceRef,
								Type:       gtfsTypeMapping[route.Type],
								Legs:       legs,
							}

							scheduleObjWriterChan <- &newSchedule
							scheduleProtoWriterChan <- &newSchedule
						}
					}
				}
			}

			var stopCount int64
			db.Model(&gtfs.Stop{}).Count(&stopCount)
			if stopCount == 0 {
				return
			}
			locationsBar := progressbar.Default(stopCount, "Generating Locations")

			stops := make([]*gtfs.Stop, 0)
			db.Find(&stops)

			for _, stop := range stops {
				newLocation := v1alphaLocations.Location{
					Id:   uuid.NewSHA1(fileNamespace, []byte(stop.Id)).String(),
					Name: stop.Name,
					Coordinates: &v1alpha.LatLng{
						Latitude:  stop.Latitude,
						Longitude: stop.Longitude,
					},
					CountryCode: "",
					TimeZone:    lookup.TimeZone(stop.Latitude, stop.Longitude),
					SourceRef:   sourceRef,
				}
				newLocation.Types = getTypeSlice(stopTypes[stop.Id])
				check(writeLocationObj(locationsObjFile, &newLocation, programStartTime))
				check(locationWriter.Write(&newLocation))
				check(locationsBar.Add(1))
			}

			check(locationsBar.Finish())
		}()
	}

	// Inform the workers to finish.
	scheduleProtoWriterChan <- nil
	scheduleObjWriterChan <- nil

	fileWriterWg.Wait()
	check(bufLocationWriter.Flush())
	close(scheduleObjWriterChan)
	close(scheduleProtoWriterChan)
}

func getOnOff(agency gtfs.Agency, stopTimes []*gtfs.StopTime, index int) (bool, bool) {
	return stopTimes[index].PickupType == 0, stopTimes[index+1].DropOffType == 0
}

func getTypeSlice(travelType locationTypesMap) []v1alphaLocations.Location_Type {
	types := make([]v1alphaLocations.Location_Type, 0, len(travelType))
	for key := range travelType {
		types = append(types, key)
	}
	return types
}
