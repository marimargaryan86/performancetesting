package main

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/merge_request"
	"git.snowfall.se/junction/junction/golang/stdlib/service"
	"github.com/getsentry/sentry-go"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/xanzy/go-gitlab"
	"go.uber.org/zap"
	"math/rand"
	"net/http"
	"time"
)

var gitlabBaseUrl string
var gitlabToken string
var httpPort int
var cmd = &cobra.Command{
	Use:   "serve",
	Short: "Listen to incoming web hooks from GitLab",
	RunE:  snowman,
	Args:  cobra.ExactArgs(0),
}

func init() {
	service.Root().AddCommand(cmd)

	cmd.PersistentFlags().StringVar(&gitlabBaseUrl, "gitlab-base-url", "", "")
	cmd.PersistentFlags().StringVar(&gitlabToken, "gitlab-token", "", "")
	cmd.PersistentFlags().IntVar(&httpPort, "http-port", 80, "")

	if err := viper.BindPFlag("gitlab_base_url", cmd.PersistentFlags().Lookup("gitlab-base-url")); err != nil {
		panic(err)
	}

	if err := viper.BindPFlag("gitlab_token", cmd.PersistentFlags().Lookup("gitlab-token")); err != nil {
		panic(err)
	}

	if err := viper.BindPFlag("http_port", cmd.PersistentFlags().Lookup("http-port")); err != nil {
		panic(err)
	}
}

func main() {
	if err := service.Root().Execute(); err != nil {
		fmt.Println(err)
	}
}

func snowman(cmd *cobra.Command, args []string) error {
	rand.Seed(time.Now().UnixNano())

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
			Release:     "snowman@" + release,
		})

		if err != nil {
			sugar.Fatal(err)
		}

		defer sentry.Flush(2 * time.Second)
	}

	client, err := gitlab.NewClient(viper.GetString("gitlab-token"), gitlab.WithBaseURL(viper.GetString("gitlab-base-url")))

	if err != nil {
		return err
	}

	mr := merge_request.MergeRequestPlugin{
		Client: client,
		Logger: sugar.Named("merge_request"),
	}

	wh := webhook{
		Logger: sugar.Named("snowman"),
		Plugins: []plugin{
			mr.OnEvent,
		},
		Secret: "",
	}

	mux := http.NewServeMux()
	mux.Handle("/", wh)

	return http.ListenAndServe(fmt.Sprintf("0.0.0.0:%d", viper.GetInt("http-port")), mux)
}
