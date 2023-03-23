package main

import (
	"fmt"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"git.snowfall.se/junction/junction/golang/cmd/snowman/merge_request"
	"git.snowfall.se/junction/junction/golang/stdlib/logging"
	"git.snowfall.se/junction/junction/golang/stdlib/service"
	"github.com/getsentry/sentry-go"
	"github.com/robfig/cron/v3"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"github.com/xanzy/go-gitlab"
	"go.uber.org/zap"
	"net/http"
	"os"
	"time"
)

var parseCmd = &cobra.Command{
	Use:   "parse",
	Short: "Parse the title of a commit message",
	RunE:  parse,
	Args:  cobra.MatchAll(cobra.ExactArgs(1), cobra.OnlyValidArgs),
}
var serveCmd = &cobra.Command{
	Use:   "serve",
	Short: "Listen to incoming web hooks from GitLab",
	RunE:  serve,
	Args:  cobra.MatchAll(cobra.ExactArgs(0), cobra.OnlyValidArgs),
}

func init() {
	var gitlabBaseUrl string
	var gitlabToken string
	var gitlabWebhookSecret string
	var httpPort int
	var snowmanHookUrl string

	service.Root().AddCommand(parseCmd)
	service.Root().AddCommand(serveCmd)

	serveCmd.PersistentFlags().StringVar(&gitlabBaseUrl, "gitlab-base-url", "", "")
	serveCmd.PersistentFlags().StringVar(&gitlabToken, "gitlab-token", "", "")
	serveCmd.PersistentFlags().StringVar(&gitlabWebhookSecret, "gitlab-webhook-secret", "", "")
	serveCmd.PersistentFlags().IntVar(&httpPort, "http-port", 80, "")
	serveCmd.PersistentFlags().StringVar(&snowmanHookUrl, "snowman-hook-url", "", "")

	if err := viper.BindPFlag("gitlab_base_url", serveCmd.PersistentFlags().Lookup("gitlab-base-url")); err != nil {
		panic(err)
	}

	if err := viper.BindPFlag("gitlab_token", serveCmd.PersistentFlags().Lookup("gitlab-token")); err != nil {
		panic(err)
	}

	if err := viper.BindPFlag("gitlab_webhook_secret", serveCmd.PersistentFlags().Lookup("gitlab-webhook-secret")); err != nil {
		panic(err)
	}

	if err := viper.BindPFlag("http_port", serveCmd.PersistentFlags().Lookup("http-port")); err != nil {
		panic(err)
	}

	if err := viper.BindPFlag("snowman_hook_url", serveCmd.PersistentFlags().Lookup("snowman-hook-url")); err != nil {
		panic(err)
	}
}

func main() {
	if err := service.Root().Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func parse(cmd *cobra.Command, args []string) error {
	title, err := common.ParseCommitTitle(args[0])

	if err != nil {
		return err
	}

	cmd.Printf("Breaking: %+v\n", title.IsBreaking)
	cmd.Printf("Description: %+v\n", title.Description)
	cmd.Printf("Draft: %+v\n", title.IsDraft)
	cmd.Printf("Scope: %+v\n", title.Scope)
	cmd.Printf("Title: %+v\n", title.Title)
	cmd.Printf("Type: %+v\n", title.Type)

	return nil
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
			Release:     "snowman@" + release,
		})

		if err != nil {
			logger.Sugar().Fatal(err)
		}

		defer sentry.Flush(2 * time.Second)
		logger = logging.ModifyToSentryLogger(logger, sentry.CurrentHub().Client())
	}

	sugar := logger.Sugar()
	c := cron.New()
	client, err := gitlab.NewClient(viper.GetString("gitlab_token"), gitlab.WithBaseURL(viper.GetString("gitlab_base_url")))

	if err != nil {
		return err
	}

	snowman, _, err := client.Users.CurrentUser()

	if err != nil {
		return err
	}

	mr := merge_request.NewPlugin(client, sugar, snowman)

	manageMemberships(client, sugar.Named("cron"), snowman, viper.GetString("snowman_hook_url"), viper.GetString("gitlab_webhook_secret"))

	if _, err = c.AddFunc("*/10 * * * *", func() {
		manageMemberships(client, sugar.Named("cron"), snowman, viper.GetString("snowman_hook_url"), viper.GetString("gitlab_webhook_secret"))
	}); err != nil {
		return err
	}

	wh := webhook{
		Logger: sugar.Named("snowman"),
		Plugins: []plugin{
			mr.OnEvent,
		},
		Secret: viper.GetString("gitlab_webhook_secret"),
	}

	go c.Start()

	mux := http.NewServeMux()
	mux.Handle("/", wh)

	return http.ListenAndServe(fmt.Sprintf("0.0.0.0:%d", viper.GetInt("http_port")), mux)
}
