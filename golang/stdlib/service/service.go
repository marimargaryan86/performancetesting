package service

import (
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"os"
	"path/filepath"
)

var logLevel string
var sentryDsn string
var rootCmd = &cobra.Command{
	Use: filepath.Base(os.Args[0]),
	PersistentPreRun: func(cmd *cobra.Command, args []string) {
		viper.SetDefault("env_name", "local")
		viper.SetDefault("platform_name", "Junction")
		viper.SetDefault("version", "dev")
		viper.SetEnvPrefix("")
		viper.AutomaticEnv()
	},
}

func init() {
	rootCmd.PersistentFlags().StringVar(&logLevel, "log-level", "", "")
	rootCmd.PersistentFlags().StringVar(&sentryDsn, "sentry-dsn", "", "")

	if err := viper.BindPFlag("log_level", rootCmd.PersistentFlags().Lookup("log-level")); err != nil {
		panic(err)
	}

	if err := viper.BindPFlag("sentry_dsn", rootCmd.PersistentFlags().Lookup("sentry-dsn")); err != nil {
		panic(err)
	}
}

func Root() *cobra.Command {
	return rootCmd
}
