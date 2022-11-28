package main

import (
	"archive/zip"
	"bufio"
	"fmt"
	"git.snowfall.se/junction/junction/golang/gtfs"
	placesv1alpha "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/service/places/v1alpha"
	v1alpha "git.snowfall.se/junction/junction/golang/protobuf/snowfall/stdlib/v1alpha"
	"git.snowfall.se/junction/junction/golang/protoio"
	"github.com/bits-and-blooms/bloom"
	"github.com/catmullet/tz"
	"github.com/google/uuid"
	"github.com/schollz/progressbar/v3"
	"google.golang.org/protobuf/types/known/timestamppb"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"io"
	"io/ioutil"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"
)

const namespace = "3cbbd269-773c-481b-bc1c-c59dfc19a063"

var gtfsTypeMapping = map[uint]v1alpha.Schedule_Type{
	0:    v1alpha.Schedule_TYPE_UNSPECIFIED,
	1:    v1alpha.Schedule_TYPE_UNSPECIFIED,
	2:    v1alpha.Schedule_TYPE_RAIL,
	3:    v1alpha.Schedule_TYPE_UNSPECIFIED,
	4:    v1alpha.Schedule_TYPE_FERRY,
	5:    v1alpha.Schedule_TYPE_UNSPECIFIED,
	6:    v1alpha.Schedule_TYPE_UNSPECIFIED,
	7:    v1alpha.Schedule_TYPE_UNSPECIFIED,
	11:   v1alpha.Schedule_TYPE_UNSPECIFIED,
	12:   v1alpha.Schedule_TYPE_UNSPECIFIED,
	100:  v1alpha.Schedule_TYPE_RAIL,
	101:  v1alpha.Schedule_TYPE_RAIL,
	102:  v1alpha.Schedule_TYPE_RAIL,
	103:  v1alpha.Schedule_TYPE_RAIL,
	104:  v1alpha.Schedule_TYPE_RAIL,
	105:  v1alpha.Schedule_TYPE_RAIL,
	106:  v1alpha.Schedule_TYPE_RAIL,
	107:  v1alpha.Schedule_TYPE_RAIL,
	108:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	109:  v1alpha.Schedule_TYPE_RAIL,
	110:  v1alpha.Schedule_TYPE_RAIL,
	111:  v1alpha.Schedule_TYPE_RAIL,
	112:  v1alpha.Schedule_TYPE_RAIL,
	113:  v1alpha.Schedule_TYPE_RAIL,
	114:  v1alpha.Schedule_TYPE_RAIL,
	115:  v1alpha.Schedule_TYPE_RAIL,
	116:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	117:  v1alpha.Schedule_TYPE_RAIL,
	200:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	201:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	202:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	203:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	204:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	205:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	206:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	207:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	208:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	209:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	400:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	401:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	402:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	403:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	404:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	405:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	700:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	701:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	702:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	703:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	704:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	705:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	706:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	707:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	708:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	709:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	710:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	711:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	712:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	713:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	714:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	715:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	716:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	800:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	900:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	901:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	902:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	903:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	904:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	905:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	906:  v1alpha.Schedule_TYPE_UNSPECIFIED,
	1000: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1100: v1alpha.Schedule_TYPE_AIR,
	1200: v1alpha.Schedule_TYPE_FERRY,
	1300: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1400: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1500: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1501: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1502: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1503: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1504: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1505: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1506: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1507: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1700: v1alpha.Schedule_TYPE_UNSPECIFIED,
	1702: v1alpha.Schedule_TYPE_UNSPECIFIED,
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

func serviceDates(serviceId string, calendarDates []*gtfs.CalendarDate, calendars []*gtfs.Calendar, timeZone *time.Location) []time.Time {
	if v, ok := serviceDateCache[serviceId]; ok {
		return v
	}

	now := time.Now()
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

			if current.Before(now) || !weekdays[current.Weekday()] {
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
			if _, ok := result[current]; ok {
				delete(result, current)
			}
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

func defaultChunkCallback[T gtfs.FileType](row T) {

}

func indexFile[T gtfs.FileType](file *zip.File, db *gorm.DB, callback func(T), filter func(T) bool) {
	var row T

	check(db.AutoMigrate(&row))

	f, err := file.Open()

	check(err)

	i := 0
	batch := make([]T, 0, db.CreateBatchSize)
	progress := progressbar.NewReader(f, progressbar.DefaultBytes(
		file.FileInfo().Size(),
		"Indexing "+file.Name,
	))

	closer := io.ReadCloser(&progress)

	defer closeFile(closer)

	br := bufio.NewReader(closer)
	next, _, err := br.ReadRune()

	check(err)

	if next != '\uFEFF' {
		check(br.UnreadRune())
	}

	r, err := gtfs.NewReader[T](br)

	check(err)

	for {
		if i != 0 && i%db.CreateBatchSize == 0 {
			db.Create(&batch)

			batch = make([]T, 0, db.CreateBatchSize)
		}

		row, err = r.Next()

		if err == io.EOF {
			break
		}

		check(err)

		if !filter(row) {
			continue
		}

		callback(row)

		batch = append(batch, row)
		i++
	}

	if len(batch) > 0 {
		db.Create(&batch)
	}
}

func main() {
	lookup, err := tz.NewTZ()

	check(err)

	schedulesFile, err := os.OpenFile("schedules_"+strconv.FormatInt(time.Now().Unix(), 10)+".bin", os.O_CREATE|os.O_WRONLY, 0644)

	check(err)

	defer closeFile(schedulesFile)

	bufScheduleWriter := bufio.NewWriter(schedulesFile)
	scheduleWriter := protoio.NewProtoWriter(bufScheduleWriter)

	placesFile, err := os.OpenFile("places_"+strconv.FormatInt(time.Now().Unix(), 10)+".bin", os.O_CREATE|os.O_WRONLY, 0644)

	check(err)

	bufPlaceWriter := bufio.NewWriter(placesFile)
	placeWriter := protoio.NewProtoWriter(bufPlaceWriter)

	defer closeFile(placesFile)

	feedFiles, err := ioutil.ReadDir("feeds/")

	check(err)

	for _, feedFileName := range feedFiles {
		if filepath.Ext(feedFileName.Name()) != ".zip" {
			continue
		}

		func() {
			serviceDateCache = make(map[string][]time.Time)
			sourceRef := strings.TrimSuffix(feedFileName.Name(), filepath.Ext(feedFileName.Name()))
			fileNamespace := uuid.NewSHA1(uuid.MustParse(namespace), []byte(sourceRef))
			zf, err := zip.OpenReader("feeds/" + sourceRef + ".zip")
			check(err)

			defer zf.Close()

			files := make(map[string]*zip.File, len(zf.File))

			for _, file := range zf.File {
				files[filepath.Base(file.Name)] = file
			}

			if _, ok := files["stop_times.txt"]; !ok {
				return
			}

			fmt.Println("--- " + sourceRef + " ---")

			tempFile, err := ioutil.TempFile("", "gtfs-import")

			check(err)
			check(tempFile.Close())

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

			indexFile[gtfs.Route](files["routes.txt"], db, func(row gtfs.Route) {
				routesFilter.AddString(row.Id)
			}, func(row gtfs.Route) bool {
				return gtfsTypeMapping[row.Type] != v1alpha.Schedule_TYPE_UNSPECIFIED
			})

			now := time.Now()
			now = time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())

			if _, ok := files["calendar.txt"]; ok {
				indexFile[gtfs.Calendar](files["calendar.txt"], db, func(row gtfs.Calendar) {
					servicesFilter.AddString(row.ServiceId)
				}, func(row gtfs.Calendar) bool {
					return now.Before(row.EndDate)
				})
			}

			if _, ok := files["calendar_dates.txt"]; ok {
				indexFile[gtfs.CalendarDate](files["calendar_dates.txt"], db, func(row gtfs.CalendarDate) {
					servicesFilter.AddString(row.ServiceId)
				}, func(row gtfs.CalendarDate) bool {
					return now.Before(row.Date)
				})
			}

			indexFile[gtfs.Trip](files["trips.txt"], db, func(row gtfs.Trip) {
				tripsFilter.AddString(row.Id)
			}, func(row gtfs.Trip) bool {
				if !routesFilter.TestString(row.RouteId) {
					return false
				}

				return servicesFilter.TestString(row.ServiceId)
			})

			indexFile[gtfs.StopTime](files["stop_times.txt"], db, func(row gtfs.StopTime) {
				stopTimesFilter.AddString(row.StopId)
			}, func(row gtfs.StopTime) bool {
				return tripsFilter.TestString(row.TripId) && (row.DropOffType == 0 || row.PickupType == 0)
			})

			indexFile[gtfs.Stop](files["stops.txt"], db, defaultChunkCallback[gtfs.Stop], func(row gtfs.Stop) bool {
				return stopTimesFilter.TestString(row.Id)
			})

			agencyFile, err := files["agency.txt"].Open()

			check(err)

			progress := progressbar.NewReader(agencyFile, progressbar.DefaultBytes(
				files["agency.txt"].FileInfo().Size(),
				"Generating schedules",
			))

			closer := io.ReadCloser(&progress)

			defer closeFile(closer)

			br := bufio.NewReader(closer)
			next, _, err := br.ReadRune()

			check(err)

			if next != '\uFEFF' {
				check(br.UnreadRune())
			}

			r, err := gtfs.NewReader[gtfs.Agency](br)

			check(err)

			for {
				agency, err := r.Next()

				if err == io.EOF {
					break
				}

				check(err)

				routes := make([]*gtfs.Route, 0)

				db.Where("agency_id = ?", agency.Id).Order("id ASC").Find(&routes)

				for _, route := range routes {
					routeName := route.ShortName

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
						}

						calendarDates := make([]*gtfs.CalendarDate, 0)

						if _, ok := files["calendar_dates.txt"]; ok {
							db.Where("service_id = ?", trip.ServiceId).Find(&calendarDates)
						}

						calendars := make([]*gtfs.Calendar, 0)

						if _, ok := files["calendar.txt"]; ok {
							db.Where("service_id = ?", trip.ServiceId).Find(&calendars)
						}

						for _, serviceDate := range serviceDates(trip.ServiceId, calendarDates, calendars, agency.Timezone) {
							legs := make([]*v1alpha.Leg, 0, len(stopTimes))
							scheduleId := uuid.NewSHA1(fileNamespace, []byte(strings.Join([]string{
								trip.Id,
								serviceDate.Format("2006-01-02"),
							}, "\x00")))

							for j := 0; j+1 < len(stopTimes); j++ {
								var departureAt *timestamppb.Timestamp
								var arrivalAt *timestamppb.Timestamp

								if stopTimes[j].PickupType == 0 {
									departureAt = timestamppb.New(serviceDate.Add(stopTimes[j].DepartureTime))
								}

								if stopTimes[j+1].DropOffType == 0 {
									arrivalAt = timestamppb.New(serviceDate.Add(stopTimes[j+1].ArrivalTime))
								}

								origin := tripStops[stopTimes[j].StopId]
								destination := tripStops[stopTimes[j+1].StopId]

								legs = append(legs, &v1alpha.Leg{
									Id: uuid.NewSHA1(scheduleId, []byte(strings.Join([]string{
										uuid.NewSHA1(fileNamespace, []byte(strings.Join([]string{
											trip.Id,
											serviceDate.Format("2006-01-02"),
											strconv.Itoa(j),
										}, "\x00"))).String(),
										uuid.NewSHA1(fileNamespace, []byte(strings.Join([]string{
											trip.Id,
											serviceDate.Format("2006-01-02"),
											strconv.Itoa(j + 1),
										}, "\x00"))).String(),
									}, "\x00"))).String(),
									Origin: &v1alpha.Point{
										Ref:  origin.Id,
										Name: origin.Name,
										Coordinates: &v1alpha.Coordinates{
											Latitude:  origin.Latitude,
											Longitude: origin.Longitude,
										},
										TimeZone: stopTz[origin.Id],
									},
									Destination: &v1alpha.Point{
										Ref:  destination.Id,
										Name: destination.Name,
										Coordinates: &v1alpha.Coordinates{
											Latitude:  destination.Latitude,
											Longitude: destination.Longitude,
										},
										TimeZone: stopTz[destination.Id],
									},
									DepartureAt: departureAt,
									ArrivalAt:   arrivalAt,
									Type:        gtfsTypeMapping[route.Type],
									AgencyName:  agency.Name,
								})
							}

							if len(legs) < 1 {
								break
							}

							check(scheduleWriter.Write(&v1alpha.Schedule{
								Id:         scheduleId.String(),
								Name:       routeName,
								AgencyName: agency.Name,
								SourceRef:  sourceRef,
								Type:       gtfsTypeMapping[route.Type],
								Legs:       legs,
							}))
						}
					}
				}
			}

			var stopCount int64

			db.Model(&gtfs.Stop{}).Count(&stopCount)

			bar := progressbar.Default(
				stopCount,
				"Generating locations",
			)

			stops := make([]*gtfs.Stop, 0)

			db.Find(&stops)

			for _, stop := range stops {
				check(placeWriter.Write(&placesv1alpha.Location{
					Id:   uuid.NewSHA1(fileNamespace, []byte(stop.Id)).String(),
					Name: stop.Name,
					Coordinates: &v1alpha.LatLng{
						Latitude:  stop.Latitude,
						Longitude: stop.Longitude,
					},
					CountryCode: "",
					TimeZone:    lookup.TimeZone(stop.Latitude, stop.Longitude),
					SourceRef:   sourceRef,
				}))
				check(bar.Add(1))
			}

			check(bar.Finish())
		}()
	}

	check(bufScheduleWriter.Flush())
	check(bufPlaceWriter.Flush())
}
