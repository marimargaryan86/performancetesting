package main

import (
	"bufio"
	_ "embed"
	"encoding/json"
	"errors"
	"fmt"
	"hash/fnv"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"git.snowfall.se/junction/junction/golang/gtfs"
	"git.snowfall.se/junction/junction/golang/ssim"
	"git.snowfall.se/junction/junction/golang/stdlib/service"
	"github.com/getsentry/sentry-go"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"go.uber.org/zap"
)

//go:embed airports.json
var airportsFile []byte

//go:embed airlines.json
var airlinesFile []byte

// global logger
var sugar *zap.SugaredLogger

type Airport struct {
	TimeZone  string  `json:"time_zone"`
	Name      string  `json:"name"`
	Longitude float64 `json:"longitude"`
	Latitude  float64 `json:"latitude"`
	IataCode  string  `json:"iata_code"`
}

var cmd = &cobra.Command{
	Use:   "convert",
	Short: "Convert a SSIM data file into a GTFS zip",
	RunE:  convert,
	Args:  cobra.ExactArgs(2),
}

func check(err error) {
	if err != nil {
		sugar.Fatal(err)
	}
}

func addVariation(d time.Duration, variation byte) (time.Duration, error) {
	switch variation {
	case 'A':
		return d, errors.New("previous day departures/arrivals not supported")
	default:
		dateVariation, err := strconv.Atoi(string(variation))
		check(err)
		return d + (24 * time.Hour * time.Duration(dateVariation)), nil
	}
}

func toTripId(v ssim.FlightLeg) string {
	// Returns an ID string based on carrier, flight number,suffix and  variation
	// e.g. BA15_8
	return fmt.Sprintf(
		"%s%d%s_%d",
		v.AirlineDesignator,
		v.FlightNumber,
		v.OperationalSuffix,
		(v.ItineraryVariationIdentifierOverflow*100)+v.ItineraryVariationIdentifier,
	)
}

func getRouteId(v *ssim.FlightLeg) string {
	return fmt.Sprintf("%s%d%s", v.AirlineDesignator, v.FlightNumber, v.OperationalSuffix)
}

func init() {
	service.Root().AddCommand(cmd)
}

func main() {
	// See go Cobra CLI Processing - this will execute _convert or _copy
	// if command verb "convert" or "copy" specified, else exits with error
	if err := service.Root().Execute(); err != nil {
		fmt.Println(err)
	}
}

func convert(_ *cobra.Command, args []string) error {
	/*
		"main", this function is run by Cobra command `go run ssim-convert.go convert input-SSIM-file output-zipfile-dir`
		args[0] is the filename of the SSIM data file (after expansion from a .gz archive), normally
			<data-root>/simsfl/SIMSFL.DAT
		args[1] is the output directory, normally <data-root>/ssim_data/
	*/
	logger, _ := zap.NewProduction()

	defer func() {
		err := logger.Sync()
		if err != nil {
			return
		}
	}()

	sugar = logger.Sugar()

	sentryDsn := viper.GetString("sentry_dsn")
	if sentryDsn != "" {
		environment := viper.GetString("env_name")
		release := viper.GetString("version")
		err := sentry.Init(sentry.ClientOptions{
			Dsn:         sentryDsn,
			Environment: environment,
			Release:     "ssim-convert@" + release,
		})

		if err != nil {
			sugar.Fatal(err)
		}

		defer sentry.Flush(2 * time.Second)
	}

	var airports []Airport
	airportsMap := make(map[string]Airport)

	if err := json.Unmarshal(airportsFile, &airports); err != nil {
		sugar.Fatal(err)
	}
	for _, a := range airports {
		airportsMap[a.IataCode] = a
	}

	var airlinesList []string
	if err := json.Unmarshal(airlinesFile, &airlinesList); err != nil {
		sugar.Fatal(err)
	}
	// Convert list to set/map
	airlinesToExport := make(map[string]bool)
	for _, a := range airlinesList {
		airlinesToExport[a] = true
	}

	parser := ssim.NewParser()
	inputFile, err := os.Open(args[0])

	if err != nil {
		sugar.Fatal(err)
	}

	defer inputFile.Close()

	results := parser.Parse(bufio.NewReader(inputFile))

	check(os.RemoveAll(args[1]))
	check(os.MkdirAll(args[1], 0755))

	var lastLeg *ssim.FlightLeg
	var zipWriter *gtfs.ZipWriter

	routeIds := make(map[string]struct{})
	serviceIds := make(map[string]struct{})
	stopIds := make(map[string]struct{})
	skipServiceTypes := make(map[string]struct{})
	for _, v := range []string{"F", "V", "M", "A", "O", "H", "P", "T", "K", "D", "E", "W", "X", "I", "N"} {
		skipServiceTypes[v] = struct{}{}
	}

ResultParser:
	for r := range results {
		check(r.Error)

		v, isFlightLegRecord := r.Record.(ssim.FlightLeg)
		_, isSegmentDataRecord := r.Record.(ssim.SegmentData)

		if lastLeg != nil {
			if isFlightLegRecord && toTripId(*lastLeg) == toTripId(v) {
				writeLegStopTime(v, lastLeg, zipWriter)
			} else if !isFlightLegRecord && !isSegmentDataRecord ||
				isFlightLegRecord && toTripId(*lastLeg) != toTripId(v) {
				writeFinalLeg(lastLeg, zipWriter)
				lastLeg = nil
			}
		}

		switch v := r.Record.(type) {
		case ssim.Schedule:
			break
		case ssim.Carrier:
			// New carrier, start a new file (and close previous one)
			if zipWriter != nil {
				check(zipWriter.Close())
			}

			if !airlinesToExport[v.AirlineDesignator] {
				zipWriter = nil
				fmt.Printf("SKIP carrier: \"%s\"\n", v.AirlineDesignator)
				continue ResultParser
			}
			delete(airlinesToExport, v.AirlineDesignator)

			zipWriter, err = gtfs.NewZipWriter(filepath.Join(args[1], "ssim-"+strings.ToLower(v.AirlineDesignator)+".zip"))
			check(err)

			lastLeg = nil
			serviceIds = make(map[string]struct{})
			routeIds = make(map[string]struct{})
			stopIds = make(map[string]struct{})

			check(zipWriter.Agency().Write(gtfs.Agency{
				Id:       v.AirlineDesignator,
				Name:     v.AirlineDesignator,
				Url:      "https://snowfalltravel.com/",
				Timezone: time.UTC,
			})) // The one and only row in the agency.txt file
			fmt.Printf("Exporting carrier: %s\n", v.AirlineDesignator)

		case ssim.FlightLeg:
			if v.AircraftOwner != "" && v.AircraftOwner != v.AirlineDesignator {
				continue ResultParser
			}

			if zipWriter == nil {
				continue ResultParser
			}
			if _, ok := skipServiceTypes[v.ServiceType]; ok {
				continue ResultParser
			}

			lastLeg = ProcessFlightLeg(&v, serviceIds, zipWriter, stopIds, airportsMap, routeIds)

		case ssim.SegmentData, ssim.Trailer:
			break

		default:
			sugar.Fatalf("Unexpected type '%T'", v)
		}
	}

	if zipWriter != nil {
		check(zipWriter.Close())
	}

	if len(airlinesToExport) > 0 {
		sugar.Fatalf("Missing expected airlines: %s", airlinesToExport)
	}

	return nil
}

func writeFinalLeg(lastLeg *ssim.FlightLeg, zipWriter *gtfs.ZipWriter) {
	depArr, err := addVariation(lastLeg.ScheduledTimeOfAircraftArrival, lastLeg.DateVariation[1])

	if err != nil {
		sugar.Fatal(err)
	}

	check(zipWriter.StopTimes().Write(gtfs.StopTime{
		TripId:            toTripId(*lastLeg),
		ArrivalTime:       depArr,
		DepartureTime:     depArr,
		StopId:            lastLeg.ArrivalStation,
		StopSequence:      uint(lastLeg.LegSequenceNumber),
		PickupType:        1,
		DropOffType:       0,
		ContinuousPickup:  1,
		ContinuousDropOff: 1,
	}))
}

func writeLegStopTime(v ssim.FlightLeg, lastLeg *ssim.FlightLeg, zipWriter *gtfs.ZipWriter) {
	dep, err := addVariation(v.ScheduledTimeOfAircraftDeparture, v.DateVariation[0])
	check(err)

	arr, err := addVariation(lastLeg.ScheduledTimeOfAircraftArrival, lastLeg.DateVariation[1])
	check(err)

	check(zipWriter.StopTimes().Write(gtfs.StopTime{
		TripId:            toTripId(v),
		ArrivalTime:       arr,
		DepartureTime:     dep,
		StopId:            lastLeg.ArrivalStation,
		StopSequence:      uint(lastLeg.LegSequenceNumber),
		PickupType:        0,
		DropOffType:       0,
		ContinuousPickup:  1,
		ContinuousDropOff: 1,
	}))
}

func ProcessFlightLeg(v *ssim.FlightLeg, serviceIds map[string]struct{}, zipWriter *gtfs.ZipWriter, stopIds map[string]struct{}, airportsMap map[string]Airport, routeIds map[string]struct{}) *ssim.FlightLeg {
	ok := false
	err := error(nil)
	calendar := gtfs.Calendar{
		Monday:    v.DaysOfOperation[0] == '1',
		Tuesday:   v.DaysOfOperation[1] == '2',
		Wednesday: v.DaysOfOperation[2] == '3',
		Thursday:  v.DaysOfOperation[3] == '4',
		Friday:    v.DaysOfOperation[4] == '5',
		Saturday:  v.DaysOfOperation[5] == '6',
		Sunday:    v.DaysOfOperation[6] == '7',
		StartDate: v.PeriodOfOperationFrom,
		EndDate:   v.PeriodOfOperationTo,
	}

	serviceId := getServiceId(calendar)

	if _, ok = serviceIds[serviceId]; !ok {
		serviceIds[serviceId] = struct{}{}
		calendar.ServiceId = serviceId
		if err = zipWriter.Calendar().Write(calendar); err != nil {
			sugar.Fatal(err)
		}
	}

	for _, station := range []string{v.DepartureStation, v.ArrivalStation} {
		if _, ok = stopIds[station]; !ok {
			stopIds[station] = struct{}{}
			writeStopDetails(airportsMap, station, zipWriter, v)
		}
	}

	routeId := getRouteId(v)
	var routeType uint
	if v.AircraftType == "BUS" {
		routeType = 3
	} else {
		routeType = 1100
	}

	if _, ok = routeIds[routeId]; !ok {
		routeIds[routeId] = struct{}{}
		check(zipWriter.Routes().Write(gtfs.Route{
			Id:                routeId,
			AgencyId:          v.AirlineDesignator,
			ShortName:         routeId,
			Type:              routeType,
			ContinuousPickup:  1,
			ContinuousDropOff: 1,
		}))
	}

	if v.LegSequenceNumber == 1 {
		tripId := toTripId(*v)

		check(zipWriter.Trips().Write(gtfs.Trip{
			Id:                   tripId,
			ServiceId:            serviceId,
			RouteId:              routeId,
			ShortName:            getRouteId(v),
			WheelchairAccessible: 0,
			BikesAllowed:         0,
		}))

		depArr, err := addVariation(v.ScheduledTimeOfAircraftDeparture, v.DateVariation[0])
		check(err)

		check(zipWriter.StopTimes().Write(gtfs.StopTime{
			// Write the first Stop for this route
			TripId:            tripId,
			ArrivalTime:       depArr,
			DepartureTime:     depArr,
			StopId:            v.DepartureStation,
			StopSequence:      0,
			PickupType:        0,
			DropOffType:       1,
			ContinuousPickup:  1,
			ContinuousDropOff: 1,
		}))
	}

	return v
}

func writeStopDetails(airportsMap map[string]Airport, station string, zipWriter *gtfs.ZipWriter, flt *ssim.FlightLeg) {
	airportDetails, ok := airportsMap[station]

	if !ok {
		// We have no details of this airport! Set to 'null' and warn
		sugar.Warnf("Unknown airport: %v, operator: %v", station, flt.AirlineDesignator)
		airportDetails = Airport{
			TimeZone:  "",
			Name:      "",
			Longitude: 0,
			Latitude:  0,
			IataCode:  station,
		}
		airportsMap[station] = airportDetails
	}

	check(zipWriter.Stops().Write(gtfs.Stop{
		Id:                 station,
		Name:               airportDetails.Name,
		Longitude:          airportDetails.Longitude,
		Latitude:           airportDetails.Latitude,
		Timezone:           airportDetails.TimeZone,
		LocationType:       1,
		WheelchairBoarding: 0,
	}))
}

func getServiceId(calendar gtfs.Calendar) string {
	serviceHash := fnv.New32a()
	_, err := serviceHash.Write([]byte(fmt.Sprint(calendar)))
	check(err)
	serviceId := strconv.Itoa(int(serviceHash.Sum32()))
	return serviceId
}
