package common

import "testing"

func TestDecodeConfiguration(t *testing.T) {
	testFile := "use_merge_train: true\ncommits:\n  scopes:\n    golang:\n      - \"golang\"\n    junction/base:\n      - \"python/snowfall/project/pss\""
	config, err := decodeConfiguration([]byte(testFile))

	if err != nil {
		t.Error(err)
	}

	if config.UseMergeTrain != true {
		t.Error("merge train is not enabled")
	}

	if len(config.Commits.Scopes) != 2 {
		t.Error("not enough scopes")
	}

	if _, ok := config.Commits.Scopes["golang"]; !ok {
		t.Error("expected scope not found")
	}

	if len(config.Commits.Scopes["golang"]) != 1 || config.Commits.Scopes["golang"][0] != "golang" {
		t.Error("expected path not found in scope")
	}
}
