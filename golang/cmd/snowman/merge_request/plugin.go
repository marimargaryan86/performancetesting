package merge_request

import (
	"git.snowfall.se/junction/junction/golang/cmd/snowman/common"
	"github.com/xanzy/go-gitlab"
	"go.uber.org/zap"
	"sync"
	"time"
)

type configCacheItem struct {
	value     common.Configuration
	fetchedAt time.Time
}

type MergeRequestPlugin struct {
	Client              *gitlab.Client
	Logger              *zap.SugaredLogger
	mu                  sync.Mutex
	Snowman             *gitlab.User
	configCache         map[int]configCacheItem
	ConfigCacheDuration time.Duration
}

type invokable func() error

func (plugin *MergeRequestPlugin) OnEvent(event interface{}) {
	plugin.mu.Lock()

	defer plugin.mu.Unlock()

	var projectId int
	var mrId int

	switch e := event.(type) {
	case *gitlab.MergeEvent:
		projectId = e.Project.ID
		mrId = e.ObjectAttributes.IID
	case *gitlab.MergeCommentEvent:
		projectId = e.ProjectID
		mrId = e.MergeRequest.IID
	case *gitlab.PipelineEvent:
		if e.MergeRequest.IID == 0 {
			return
		}

		projectId = e.Project.ID
		mrId = e.MergeRequest.IID
	default:
		return
	}

	var mr *gitlab.MergeRequest
	var err error

	for {
		mr, _, err = plugin.Client.MergeRequests.GetMergeRequestChanges(
			projectId,
			mrId,
			&gitlab.GetMergeRequestChangesOptions{},
		)

		if err != nil {
			plugin.Logger.Error(err)
			return
		}

		if mr.MergeStatus != "checking" && mr.MergeStatus != "unchecked" {
			break
		}

		plugin.Logger.With("project", mr.ProjectID, "IID", mr.IID).Debug("merge status unclear, waiting.")
		time.Sleep(2 * time.Second)
	}

	logger := plugin.Logger.With("project", mr.ProjectID, "IID", mr.IID)
	val, found := plugin.configCache[mr.ProjectID]

	var config common.Configuration

	if !found || time.Now().Sub(val.fetchedAt) > plugin.ConfigCacheDuration {
		config, err = common.LoadConfiguration(plugin.Client, mr.ProjectID)

		if err != nil {
			logger.Error(err)
		} else {
			plugin.configCache[mr.ProjectID] = configCacheItem{
				value:     config,
				fetchedAt: time.Now(),
			}
		}
	} else {
		config = val.value
	}

	wrapper := &mergeRequest{
		cache:         &cache{},
		configuration: config,
		client:        plugin.Client,
		logger:        logger,
		object:        mr,
		snowman:       plugin.Snowman,
	}

	for _, i := range []invokable{
		wrapper.validateTitle,
		wrapper.validateScope,
		wrapper.setReviewers,
		wrapper.setAssignees,
		wrapper.setStatus,
		wrapper.merge,
	} {
		if err = i(); err != nil {
			logger.Error(err)
		}

		if wrapper.hasChanged {
			logger.Debug("Changes detected, skipping.")
			return // No need to run further since the changes will have triggered another event.
		}
	}
}
