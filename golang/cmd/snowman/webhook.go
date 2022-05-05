package main

import (
	"errors"
	"github.com/xanzy/go-gitlab"
	"go.uber.org/zap"
	"io"
	"io/ioutil"
	"net/http"
	"strings"
)

type plugin func(event interface{})

type webhook struct {
	Logger  *zap.SugaredLogger
	Plugins []plugin
	Secret  string
}

func (hook webhook) ServeHTTP(writer http.ResponseWriter, request *http.Request) {
	event, err := hook.parse(request)

	if err != nil {
		hook.Logger.Warn(err)
		writer.WriteHeader(400)
		return
	}

	for _, p := range hook.Plugins {
		go p(event)
	}

	writer.WriteHeader(204)
}

func (hook webhook) parse(r *http.Request) (interface{}, error) {
	defer func() {
		if _, err := io.Copy(ioutil.Discard, r.Body); err != nil {
			hook.Logger.Error(err)
		}

		if err := r.Body.Close(); err != nil {
			hook.Logger.Error(err)
		}
	}()

	if r.Method != http.MethodPost {
		return nil, errors.New("invalid HTTP Method")
	}

	if len(hook.Secret) > 0 {
		signature := r.Header.Get("X-Gitlab-Token")

		if signature != hook.Secret {
			return nil, errors.New("token validation failed")
		}
	}

	event := r.Header.Get("X-Gitlab-Event")

	if strings.TrimSpace(event) == "" {
		return nil, errors.New("missing X-Gitlab-Event Header")
	}

	eventType := gitlab.EventType(event)

	hook.Logger.With("type", eventType).Info("Event received.")

	payload, err := ioutil.ReadAll(r.Body)

	if err != nil || len(payload) == 0 {
		return nil, errors.New("error reading request body")
	}

	return gitlab.ParseWebhook(eventType, payload)
}
