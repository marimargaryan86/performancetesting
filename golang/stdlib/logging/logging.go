package logging

import (
	"github.com/TheZeroSlave/zapsentry"
	"github.com/getsentry/sentry-go"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

func ModifyToSentryLogger(log *zap.Logger, client *sentry.Client) *zap.Logger {
	core, _ := zapsentry.NewCore(
		zapsentry.Configuration{
			Level:             zapcore.ErrorLevel,
			EnableBreadcrumbs: true,
			BreadcrumbLevel:   zapcore.InfoLevel,
		},
		zapsentry.NewSentryClientFromClient(client),
	)

	log = zapsentry.AttachCoreToLogger(core, log)

	return log.With(zapsentry.NewScope())
}
