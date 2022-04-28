package main

import (
	"bufio"
	_ "embed"
	"encoding/json"
	"errors"
	"fmt"
	"git.snowfall.se/junction/junction/golang/gtfs"
	"git.snowfall.se/junction/junction/golang/ssim"
	"git.snowfall.se/junction/junction/golang/stdlib/service"
	"github.com/getsentry/sentry-go"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"go.uber.org/zap"
	"hash/fnv"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

//go:embed airports.json
var airportsFile []byte

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

func addVariation(d time.Duration, variation byte) (time.Duration, error) {
	switch variation {
	case 'A':
		return d, errors.New("previous day departures/arrivals not supported")
	default:
		dateVariation, err := strconv.Atoi(string(variation))

		if err != nil {
			return d, err
		}

		return d + (24 * time.Hour * time.Duration(dateVariation)), nil
	}
}

func toTripId(v ssim.FlightLeg) string {
	return fmt.Sprintf(
		"%s%d%s_%d",
		v.AirlineDesignator,
		v.FlightNumber,
		v.OperationalSuffix,
		(v.ItineraryVariationIdentifierOverflow*100)+v.ItineraryVariationIdentifier,
	)
}

func init() {
	service.Root().AddCommand(cmd)
}

func main() {
	if err := service.Root().Execute(); err != nil {
		fmt.Println(err)
	}
}

func convert(cmd *cobra.Command, args []string) error {
	logger, _ := zap.NewProduction()

	defer func() {
		err := logger.Sync()

		if err != nil {
			return
		}
	}()

	sugar := logger.Sugar()

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

	parser := ssim.NewParser()
	f, err := os.Open(args[0])

	if err != nil {
		sugar.Fatal(err)
	}

	defer f.Close()

	results := parser.Parse(bufio.NewReader(f))

	if err = os.RemoveAll(args[1]); err != nil {
		sugar.Fatal(err)
	}

	if err = os.MkdirAll(args[1], 0755); err != nil {
		sugar.Fatal(err)
	}

	var lastLeg *ssim.FlightLeg
	var zipWriter *gtfs.ZipWriter

	routeIds := make(map[string]struct{})
	serviceIds := make(map[string]struct{})
	stopIds := make(map[string]struct{})

ResultParser:
	for r := range results {
		if r.Error != nil {
			sugar.Fatal(r.Error)
		}

		v, ok := r.Record.(ssim.FlightLeg)
		_, ok2 := r.Record.(ssim.SegmentData)

		if lastLeg != nil && ok && toTripId(*lastLeg) == toTripId(v) {
			dep, err := addVariation(v.ScheduledTimeOfAircraftDeparture, v.DateVariation[0])

			if err != nil {
				sugar.Fatal(err)
			}

			arr, err := addVariation(lastLeg.ScheduledTimeOfAircraftArrival, lastLeg.DateVariation[1])

			if err != nil {
				sugar.Fatal(err)
			}

			if err = zipWriter.StopTimes().Write(gtfs.StopTime{
				TripId:            toTripId(v),
				ArrivalTime:       arr,
				DepartureTime:     dep,
				StopId:            lastLeg.ArrivalStation,
				StopSequence:      uint(lastLeg.LegSequenceNumber),
				PickupType:        1,
				DropOffType:       1,
				ContinuousPickup:  1,
				ContinuousDropOff: 1,
			}); err != nil {
				sugar.Fatal(err)
			}
		} else if lastLeg != nil && (!ok && !ok2 || ok && toTripId(*lastLeg) != toTripId(v)) {
			depArr, err := addVariation(lastLeg.ScheduledTimeOfAircraftArrival, lastLeg.DateVariation[1])

			if err != nil {
				sugar.Fatal(err)
			}

			if err = zipWriter.StopTimes().Write(gtfs.StopTime{
				TripId:            toTripId(*lastLeg),
				ArrivalTime:       depArr,
				DepartureTime:     depArr,
				StopId:            lastLeg.ArrivalStation,
				StopSequence:      uint(lastLeg.LegSequenceNumber),
				PickupType:        1,
				DropOffType:       0,
				ContinuousPickup:  1,
				ContinuousDropOff: 1,
			}); err != nil {
				sugar.Fatal(err)
			}

			lastLeg = nil
		}

		switch v := r.Record.(type) {
		case ssim.Schedule:
			break
		case ssim.Carrier:
			if zipWriter != nil {
				zipWriter.Close()
			}

			zipWriter, err = gtfs.NewZipWriter(filepath.Join(args[1], "ssim-"+strings.ToLower(v.AirlineDesignator)+".zip"))

			if err != nil {
				sugar.Fatal(err)
			}

			lastLeg = nil
			serviceIds = make(map[string]struct{})
			routeIds = make(map[string]struct{})
			stopIds = make(map[string]struct{})

			err = zipWriter.Agency().Write(gtfs.Agency{
				Name:     "Snowfall",
				Url:      "https://snowfalltravel.com/",
				Timezone: "UTC",
			})

			if err != nil {
				sugar.Fatal(err)
			}

		case ssim.FlightLeg:
			for _, serviceType := range []string{
				"F",
				"V",
				"M",
				"A",
				"O",
				"H",
				"P",
				"T",
				"K",
				"D",
				"E",
				"W",
				"X",
				"I",
				"N",
			} {
				if v.ServiceType == serviceType {
					continue ResultParser
				}
			}

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

			serviceHash := fnv.New32a()
			serviceHash.Write([]byte(fmt.Sprint(calendar)))
			serviceId := strconv.Itoa(int(serviceHash.Sum32()))

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

					a, ok := airportsMap[station]

					if !ok {
						sugar.Warn(station)
						a = Airport{
							TimeZone:  "",
							Name:      "",
							Longitude: 0,
							Latitude:  0,
							IataCode:  station,
						}

						airportsMap[station] = a
					}

					if err = zipWriter.Stops().Write(gtfs.Stop{
						Id:                 station,
						Name:               a.Name,
						Longitude:          a.Longitude,
						Latitude:           a.Latitude,
						Timezone:           a.TimeZone,
						LocationType:       1,
						WheelchairBoarding: 0,
					}); err != nil {
						sugar.Fatal(err)
					}
				}
			}

			routeId := fmt.Sprintf("%s%d%s", v.AirlineDesignator, v.FlightNumber, v.OperationalSuffix)

			if _, ok = routeIds[routeId]; !ok {
				routeIds[routeId] = struct{}{}
				if err = zipWriter.Routes().Write(gtfs.Route{
					Id:                routeId,
					ShortName:         routeId,
					Type:              1100,
					ContinuousPickup:  1,
					ContinuousDropOff: 1,
				}); err != nil {
					sugar.Fatal(err)
				}
			}

			if v.LegSequenceNumber == 1 {
				tripId := toTripId(v)

				if err = zipWriter.Trips().Write(gtfs.Trip{
					Id:                   tripId,
					ServiceId:            serviceId,
					RouteId:              routeId,
					ShortName:            fmt.Sprintf("%s%d%s", v.AirlineDesignator, v.FlightNumber, v.OperationalSuffix),
					WheelchairAccessible: 0,
					BikesAllowed:         0,
				}); err != nil {
					sugar.Fatal(err)
				}

				depArr, err := addVariation(v.ScheduledTimeOfAircraftDeparture, v.DateVariation[0])

				if err != nil {
					sugar.Fatal(err)
				}

				if err = zipWriter.StopTimes().Write(gtfs.StopTime{
					TripId:            tripId,
					ArrivalTime:       depArr,
					DepartureTime:     depArr,
					StopId:            v.DepartureStation,
					StopSequence:      0,
					PickupType:        0,
					DropOffType:       1,
					ContinuousPickup:  1,
					ContinuousDropOff: 1,
				}); err != nil {
					sugar.Fatal(err)
				}
			}

			lastLeg = &v
		case ssim.SegmentData:
			break
		case ssim.Trailer:
			break
		default:
			sugar.Fatalf("Unexpected type '%T'", v)
		}
	}

	if zipWriter != nil {
		zipWriter.Close()
	}

	return nil
}
