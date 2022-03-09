package main

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/legacy"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/junction/planner/v1alpha"
	"git.snowfall.se/junction/junction/golang/raptor"
	"github.com/uber/h3-go"
	"go.uber.org/zap"
	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	healthgrpc "google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection"
	"net"
	"os"
	"strconv"
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

	protoDir, ok := os.LookupEnv("PROTO_DIR")

	if !ok {
		protoDir = "./"
	}

	routes, routeSegments, stops, transfers, trips, tripSegments, err := legacy.Load(sugar, protoDir)

	if err != nil {
		sugar.Fatal(err)
	}

	grpcAddress, ok := os.LookupEnv("GRPC_ADDRESS")

	if !ok {
		grpcAddress = "0.0.0.0"
	}

	grpcPort, ok := os.LookupEnv("GRPC_PORT")

	if !ok {
		grpcPort = "50053"
	}

	lis, err := net.Listen("tcp", fmt.Sprintf("%s:%s", grpcAddress, grpcPort))

	if err != nil {
		sugar.Fatal(err)
	}

	stopsMap := make(map[h3.H3Index][]*planner.Stop, len(stops))

	for _, stop := range stops {
		intIndex, _ := strconv.Atoi(stop.Id)
		index := h3.H3Index(intIndex)

		if _, ok := stopsMap[index]; !ok {
			stopsMap[index] = make([]*planner.Stop, 0)
		}

		stopsMap[index] = append(stopsMap[index], stop)
	}

	grpcServer := grpc.NewServer()
	healthgrpc.RegisterHealthServer(grpcServer, health.NewServer())
	planner.RegisterPlannerServiceServer(grpcServer, &PlannerServiceServer{
		Planner: raptor.NewPlanner(legacy.NewRepository(routes, routeSegments, stops, transfers, trips, tripSegments), sugar),
		Stops:   stopsMap,
	})
	reflection.Register(grpcServer)

	sugar.Infow("gRPC server starting", "address", grpcAddress, "port", grpcPort)

	if err != grpcServer.Serve(lis) {
		sugar.Fatal(err)
	}
}
