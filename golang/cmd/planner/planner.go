package main

import (
    "fmt"
    "git.snowfall.se/junction/junction/golang/legacy"
    plannerv1 "git.snowfall.se/junction/junction/golang/protobuf/snowfall/junction/planner/v1"
    "git.snowfall.se/junction/junction/golang/raptor"
    "github.com/uber/h3-go"
    "go.uber.org/zap"
    "google.golang.org/grpc"
    "google.golang.org/grpc/health"
    healthgrpc "google.golang.org/grpc/health/grpc_health_v1"
    "google.golang.org/grpc/reflection"
    "io"
    "net"
    "net/http"
    "net/url"
    "os"
    "path"
    "sync"
    "time"
)

func main() {
	logger, _ := zap.NewProduction()

	defer func() {
		err := logger.Sync()

		if err != nil {
			panic(err)
		}
	}()

	sugar := logger.Sugar()

	var wg sync.WaitGroup

	for _, file := range []string{
		"https://sf-junction-data.s3.eu-north-1.amazonaws.com/proto/route_segments.bin",
		"https://sf-junction-data.s3.eu-north-1.amazonaws.com/proto/routes.bin",
		"https://sf-junction-data.s3.eu-north-1.amazonaws.com/proto/stops.bin",
		"https://sf-junction-data.s3.eu-north-1.amazonaws.com/proto/transfers.bin",
		"https://sf-junction-data.s3.eu-north-1.amazonaws.com/proto/trip_segments.bin",
		"https://sf-junction-data.s3.eu-north-1.amazonaws.com/proto/trips.bin",
	} {
		wg.Add(1)

		go func(file string) {
			u, err := url.Parse(file)

			if err != nil {
				sugar.Fatal(err)
			}

			var code int

			code, err = downloadFile(u, path.Base(file))

			if err != nil {
				sugar.Fatal(err)
			}

			sugar.Infow("file downloaded", "url", file, "code", code)

			wg.Done()
		}(file)
	}

	wg.Wait()

	routes, routeSegments, stops, transfers, trips, tripSegments, err := legacy.Load(sugar, "./")

	if err != nil {
		sugar.Fatal(err)
	}

    grpcAddress, ok := os.LookupEnv("GRPC_ADDRESS")

    if !ok {
        grpcAddress = "0.0.0.0"
    }

    grpcPort, ok := os.LookupEnv("GRPC_PORT")

    if !ok {
        grpcPort = "50051"
    }

	lis, err := net.Listen("tcp", fmt.Sprintf("%s:%s", grpcAddress, grpcPort))

	if err != nil {
		sugar.Fatal(err)
	}

	stopsMap := make(map[h3.H3Index][]*legacy.Stop, len(stops))

	for _, stop := range stops {
		index := h3.FromGeo(h3.GeoCoord{
			Latitude:  stop.Latitude,
			Longitude: stop.Longitude,
		}, 9)

		if _, ok := stopsMap[index]; !ok {
			stopsMap[index] = make([]*legacy.Stop, 0)
		}

		stopsMap[index] = append(stopsMap[index], stop)
	}

	grpcServer := grpc.NewServer()
    healthgrpc.RegisterHealthServer(grpcServer, health.NewServer())
	plannerv1.RegisterPlannerServiceServer(grpcServer, &PlannerServiceServer{
		Planner: raptor.NewPlanner(legacy.NewRepository(routes, routeSegments, stops, transfers, trips, tripSegments), sugar),
		Stops:   stopsMap,
	})
	reflection.Register(grpcServer)

	sugar.Infow("gRPC server starting", "address", grpcAddress, "port", grpcPort)

	if err != grpcServer.Serve(lis) {
		sugar.Fatal(err)
	}
}

func downloadFile(fileUrl *url.URL, filePath string) (int, error) {
	fileInfo, err := os.Stat(filePath)
	headers := map[string][]string{}

	if err == nil {
		gmt, err := time.LoadLocation("GMT")

		if err != nil {
			return 0, fmt.Errorf("unable to load GMT: %v", err)
		}

		headers["If-Modified-Since"] = []string{fileInfo.ModTime().In(gmt).Format(time.RFC1123)}
	} else if !os.IsNotExist(err) {
		return 0, fmt.Errorf("unable to open file: %v", err)
	}

	req := &http.Request{
		Method: http.MethodGet,
		URL:    fileUrl,
		Header: headers,
	}

	res, err := http.DefaultClient.Do(req)

	if err != nil {
		return 0, fmt.Errorf("download failed: %v", err)
	}

	if res.StatusCode == 200 {
		err = os.Remove(filePath)

		if err != nil && !os.IsNotExist(err) {
			return 0, fmt.Errorf("unable to delete file: %v", err)
		}

		file, err := os.Create(filePath)

		if err != nil {
			return 0, fmt.Errorf("unable to create file: %v", err)
		}

		defer file.Close()

		_, err = io.Copy(file, res.Body)

		if err != nil {
			return 0, err
		}
	} else if res.StatusCode != 304 {
		return 0, fmt.Errorf("unexpected status code: %v", res.StatusCode)
	}

	return res.StatusCode, nil
}
