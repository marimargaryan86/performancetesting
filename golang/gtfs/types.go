package gtfs

import (
	"image/color"
	"net/url"
	"time"
)

type TransferType uint
type ExceptionType uint

const (
	Recommended TransferType = iota
	Timed
	Minimum
	Impossible
)

const (
	Added ExceptionType = iota
	Removed
)

type Agency struct {
	Id       string         `csv:"agency_id,omitempty"`
	Name     string         `csv:"agency_name"`
	Url      *url.URL       `csv:"agency_url"`
	Timezone *time.Location `csv:"agency_timezone"`
	Language string         `csv:"agency_lang,omitempty"`
	Phone    string         `csv:"agency_phone,omitempty"`
	FareUrl  *url.URL       `csv:"agency_fare_url,omitempty"`
	Email    string         `csv:"agency_email,omitempty"`
}

type Calendar struct {
	ServiceId string `csv:"service_id"`
	Monday    bool   `csv:"monday"`
	Tuesday   bool   `csv:"tuesday"`
	Wednesday bool   `csv:"wednesday"`
	Thursday  bool   `csv:"thursday"`
	Friday    bool   `csv:"friday"`
	Saturday  bool   `csv:"saturday"`
	Sunday    bool   `csv:"sunday"`
	StartDate string `csv:"start_date"`
	EndDate   string `csv:"end_date"`
}

type CalendarDate struct {
	ServiceId     string        `csv:"service_id"`
	Date          string        `csv:"date"`
	ExceptionType ExceptionType `csv:"exception_type"`
}

type Route struct {
	Id                string       `csv:"route_id"`
	AgencyId          string       `csv:"agency_id,omitempty"`
	ShortName         string       `csv:"route_short_name,omitempty"`
	LongName          string       `csv:"route_long_name,omitempty"`
	Description       string       `csv:"route_desc,omitempty"`
	Type              uint         `csv:"route_type"`
	Url               *url.URL     `csv:"route_url,omitempty"`
	Color             *color.Color `csv:"route_color,omitempty"`
	TextColor         *color.Color `csv:"route_text_color,omitempty"`
	SortOrder         uint         `csv:"route_sort_order,omitempty"`
	ContinuousPickup  uint         `csv:"continuous_pickup,omitempty"`
	ContinuousDropOff uint         `csv:"continuous_drop_off,omitempty"`
}

type Stop struct {
	Id                 string         `csv:"stop_id"`
	Code               string         `csv:"stop_code,omitempty"`
	Name               string         `csv:"stop_name,omitempty"`
	Description        string         `csv:"stop_desc,omitempty"`
	Latitude           float64        `csv:"stop_lat,omitempty"`
	Longitude          float64        `csv:"stop_lon,omitempty"`
	ZoneId             string         `csv:"zone_id,omitempty"`
	Url                *url.URL       `csv:"stop_url,omitempty"`
	LocationType       uint           `csv:"location_type,omitempty"`
	ParentStation      string         `csv:"parent_station,omitempty"`
	Timezone           *time.Location `csv:"stop_timezone,omitempty"`
	WheelchairBoarding uint           `csv:"wheelchair_boarding,omitempty"`
	LevelId            string         `csv:"level_id,omitempty"`
	PlatformCode       string         `csv:"platform_code,omitempty"`
}

type StopTime struct {
	TripId            string  `csv:"trip_id"`
	ArrivalTime       string  `csv:"arrival_time,omitempty"`
	DepartureTime     string  `csv:"departure_time,omitempty"`
	StopId            string  `csv:"stop_id"`
	StopSequence      uint    `csv:"stop_sequence"`
	StopHeadsign      string  `csv:"stop_headsign,omitempty"`
	PickupType        uint    `csv:"pickup_type,omitempty"`
	DropOffType       uint    `csv:"drop_off_type,omitempty"`
	ContinuousPickup  uint    `csv:"continuous_pickup,omitempty"`
	ContinuousDropOff uint    `csv:"continuous_drop_off,omitempty"`
	ShapeDistTraveled float64 `csv:"shape_dist_traveled,omitempty"`
	Timepoint         uint    `csv:"timepoint,omitempty"`
}

type Transfer struct {
	FromStopId      string       `csv:"from_stop_id"`
	ToStopId        string       `csv:"to_stop_id"`
	Type            TransferType `csv:"transfer_type"`
	MinTransferTime uint         `csv:"min_transfer_time,omitempty"`
}

type Trip struct {
	RouteId              string `csv:"route_id"`
	ServiceId            string `csv:"service_id"`
	Id                   string `csv:"trip_id"`
	Headsign             string `csv:"trip_headsign,omitempty"`
	ShortName            string `csv:"trip_short_name,omitempty"`
	DirectionId          uint   `csv:"direction_id,omitempty"`
	BlockId              string `csv:"block_id,omitempty"`
	ShapeId              string `csv:"shape_id,omitempty"`
	WheelchairAccessible uint   `csv:"wheelchair_accessible,omitempty"`
	BikesAllowed         uint   `csv:"bikes_allowed,omitempty"`
}
