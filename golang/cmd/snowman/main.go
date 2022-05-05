package main

import (
	"git.snowfall.se/junction/junction/golang/cmd/snowman/merge_request"
	"github.com/xanzy/go-gitlab"
	"go.uber.org/zap"
	"math/rand"
	"net/http"
	"time"
)

func main() {
	rand.Seed(time.Now().UnixNano())

	logger, _ := zap.NewDevelopment()

	defer func() {
		err := logger.Sync()

		if err != nil {
			return
		}
	}()

	sugar := logger.Sugar()

	client, err := gitlab.NewClient("", gitlab.WithBaseURL(""))

	if err != nil {
		sugar.Fatal(err)
	}

	mr := merge_request.MergeRequestPlugin{
		Client: client,
		Logger: sugar.Named("merge_request"),
	}

	//mr.Test(253)
	//return

	wh := webhook{
		Logger: sugar.Named("snowman"),
		Plugins: []plugin{
			mr.OnEvent,
		},
		Secret: "",
	}

	mux := http.NewServeMux()
	mux.Handle("/", wh)
	if err := http.ListenAndServe("0.0.0.0:8080", mux); err != nil {
		sugar.Fatal(err)
	}
}
