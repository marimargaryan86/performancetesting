package main

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/legacy"
	planner "git.snowfall.se/junction/junction/golang/protobuf/snowfall/project/junction/go/service/planner/v1"
	"git.snowfall.se/junction/junction/golang/raptor"
	"git.snowfall.se/junction/junction/golang/stdlib/logging"
	"git.snowfall.se/junction/junction/golang/stdlib/service"
	"github.com/getsentry/sentry-go"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/uber/h3-go/v4"
	"go.uber.org/zap"
	"google.golang.org/grpc"
	"google.golang.org/grpc/health"
	healthgrpc "google.golang.org/grpc/health/grpc_health_v1"
	"google.golang.org/grpc/reflection"
	"net"
	"net/http"
	"os"
	"strconv"
	"time"
)

var serveCmd = &cobra.Command{
	Use:   "serve",
	Short: "Listen to incoming gRPC traffic",
	RunE:  serve,
	Args:  cobra.MatchAll(cobra.ExactArgs(0), cobra.OnlyValidArgs),
}

func init() {
	var grpcPort int
	var prometheusPort int
	var protoDir string

	service.Root().AddCommand(serveCmd)

	serveCmd.PersistentFlags().IntVar(&grpcPort, "grpc-port", 50053, "")
	serveCmd.PersistentFlags().IntVar(&prometheusPort, "prometheus-port", 0, "")
	serveCmd.PersistentFlags().StringVar(&protoDir, "proto-dir", "./", "")

	if err := viper.BindPFlag("grpc_port", serveCmd.PersistentFlags().Lookup("grpc-port")); err != nil {
		panic(err)
	}

	if err := viper.BindPFlag("prometheus_port", serveCmd.PersistentFlags().Lookup("prometheus-port")); err != nil {
		panic(err)
	}

	if err := viper.BindPFlag("proto_dir", serveCmd.PersistentFlags().Lookup("proto-dir")); err != nil {
		panic(err)
	}
}

func main() {
	if err := service.Root().Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func serve(cmd *cobra.Command, args []string) error {
	logger, _ := zap.NewProduction()

	defer func() {
		err := logger.Sync()

		if err != nil {
			return
		}
	}()

	sentryDsn := viper.GetString("sentry_dsn")

	if sentryDsn != "" {
		environment := viper.GetString("env_name")
		release := viper.GetString("version")
		err := sentry.Init(sentry.ClientOptions{
			Dsn:         sentryDsn,
			Environment: environment,
			Release:     "planner@" + release,
		})

		if err != nil {
			logger.Sugar().Fatal(err)
		}

		defer sentry.Flush(2 * time.Second)
		logger = logging.ModifyToSentryLogger(logger, sentry.CurrentHub().Client())
	}

	sugar := logger.Sugar()

	routes, routeSegments, stops, transfers, trips, tripSegments, err := legacy.Load(sugar, viper.GetString("proto_dir"))

	if err != nil {
		return err
	}

	repository, err := legacy.NewRepository(routes, routeSegments, stops, transfers, trips, tripSegments)

	if err != nil {
		return err
	}

	lis, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%d", viper.GetInt("grpc_port")))

	if err != nil {
		return err
	}

	stopsMap := make(map[h3.Cell][]*planner.Stop, len(stops))

	for _, stop := range stops {
		intIndex, _ := strconv.Atoi(stop.Id)
		index := h3.Cell(intIndex)

		if _, ok := stopsMap[index]; !ok {
			stopsMap[index] = make([]*planner.Stop, 0)
		}

		stopsMap[index] = append(stopsMap[index], stop)
	}

	grpcServer := grpc.NewServer()
	healthgrpc.RegisterHealthServer(grpcServer, health.NewServer())
	planner.RegisterPlannerServiceServer(grpcServer, &PlannerServiceServer{
		Planner: raptor.NewPlanner(repository, stopsMap, sugar),
		Stops:   stopsMap,
	})
	reflection.Register(grpcServer)

	prometheusPort := viper.GetInt("prometheus_port")

	if prometheusPort != 0 {
		go func() {
			http.Handle("/metrics", promhttp.Handler())

			if err := http.ListenAndServe(fmt.Sprintf("0.0.0.0:%d", prometheusPort), nil); err != nil {
				sugar.Fatal(err)
			}
		}()
	}

	sugar.Infow("gRPC server starting", "port", viper.GetInt("grpc_port"))

	return grpcServer.Serve(lis)
}
