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

type timerKey struct {
	projectId      int
	mergeRequestId int
}

type MergeRequestPlugin struct {
	client              *gitlab.Client
	logger              *zap.SugaredLogger
	mu                  sync.Mutex
	timers              map[timerKey]*time.Timer
	snowman             *gitlab.User
	configCache         map[int]configCacheItem
	configCacheDuration time.Duration
}

func NewPlugin(client *gitlab.Client, logger *zap.SugaredLogger, snowman *gitlab.User) *MergeRequestPlugin {
	return &MergeRequestPlugin{
		client:              client,
		logger:              logger.Named("merge_request"),
		timers:              make(map[timerKey]*time.Timer, 0),
		snowman:             snowman,
		configCache:         make(map[int]configCacheItem, 0),
		configCacheDuration: time.Minute * 10,
	}
}

const debounceTime = 10 * time.Second

func (plugin *MergeRequestPlugin) onTimer(pid int, iid int) {
	var mr *gitlab.MergeRequest
	var err error

	for {
		mr, _, err = plugin.client.MergeRequests.GetMergeRequestChanges(
			pid,
			iid,
			&gitlab.GetMergeRequestChangesOptions{},
		)

		if err != nil {
			plugin.logger.Error(err)
			return
		}

		if mr.MergeStatus != "checking" && mr.MergeStatus != "unchecked" {
			break
		}

		plugin.logger.With("project", mr.ProjectID, "IID", mr.IID).Debug("merge status unclear, waiting.")
		time.Sleep(2 * time.Second)
	}

	logger := plugin.logger.With("project", mr.ProjectID, "IID", mr.IID)
	val, found := plugin.configCache[mr.ProjectID]

	var config common.Configuration

	if !found || time.Now().Sub(val.fetchedAt) > plugin.configCacheDuration {
		config, err = common.LoadConfiguration(plugin.client, mr.ProjectID)

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
		client:        plugin.client,
		logger:        logger,
		object:        mr,
		snowman:       plugin.snowman,
	}

	title, err := common.ParseCommitTitle(wrapper.object.Title)

	if err == nil {
		wrapper.breaking = title.IsBreaking
	}

	for _, i := range []invokable{
		wrapper.validateTitle,
		wrapper.validateScope,
		wrapper.setReviewers,
		wrapper.setStatus,
		wrapper.setAssignees,
		wrapper.informBreakingChanges,
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

	key := timerKey{
		projectId:      projectId,
		mergeRequestId: mrId,
	}

	if t, ok := plugin.timers[key]; !ok {
		plugin.timers[key] = time.AfterFunc(debounceTime, func() {
			plugin.onTimer(projectId, mrId)
		})
	} else {
		t.Reset(debounceTime)
	}
}
