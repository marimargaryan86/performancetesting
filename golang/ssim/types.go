package ssim

import "time"

const titleOfContents = "AIRLINE STANDARD SCHEDULE DATA SET"

const (
	headerRecord      = '1'
	carrierRecord     = '2'
	flightLegRecord   = '3'
	segmentDataRecord = '4'
	trailerRecord     = '5'
)

const (
	Local = iota
	Utc
)

const (
	Confirmed = iota
	Provisional
)

const (
	Continuation = iota
	End
)

type Schedule struct {
	TitleOfContents     string
	NumberOfSeasons     uint8
	DataSetSerialNumber uint16
	RecordSerialNumber  uint32
	Carriers            []*Carrier
}

type Carrier struct {
	TimeMode                       int
	ScheduleStatus                 int
	RecordSerialNumber             uint32
	AirlineDesignator              string
	Season                         string
	TitleOfData                    string
	CreatorReference               string
	GeneralInformation             string
	InFlightServiceInformation     string
	ElectronicTicketingInformation string
	ScheduleValidFrom              time.Time
	ScheduleValidTo                time.Time
	CreationDate                   time.Time
	ReleaseSellDate                time.Time
	DuplicateAirlineDesignator     bool
	FlightLegs                     []*FlightLeg
}

type FlightLeg struct {
	OperationalSuffix                          string
	AirlineDesignator                          string
	FlightNumber                               int
	ItineraryVariationIdentifier               int
	LegSequenceNumber                          int
	ServiceType                                string
	PeriodOfOperationFrom                      time.Time
	PeriodOfOperationTo                        time.Time
	DaysOfOperation                            string
	FrequencyRate                              int
	DepartureStation                           string
	ScheduledTimeOfPassengerDeparture          time.Duration
	ScheduledTimeOfAircraftDeparture           time.Duration
	UtcLocalTimeVariationDepartureStation      string
	PassengerTerminalDepartureStation          string
	ArrivalStation                             string
	ScheduledTimeOfAircraftArrival             time.Duration
	ScheduledTimeOfPassengerArrival            time.Duration
	UtcLocalTimeVariationArrivalStation        string
	PassengerTerminalArrivalStation            string
	AircraftType                               string
	PassengerReservationsBookingDesignator     string
	PassengerReservationsBookingModifier       string
	MealServiceNote                            string
	JointOperationAirlineDesignators           string
	MinimumConnectingTimeStatus                string
	SecureFlightIndicator                      string
	ItineraryVariationIdentifierOverflow       string
	AircraftOwner                              string
	CockpitCrewEmployer                        string
	CabinCrewEmployer                          string
	OnwardFlightAirlineDesignator              string
	OnwardFlightFlightNumber                   int
	OnwardFlightAircraftRotationLayover        string
	OnwardFlightOperationalSuffix              string
	FlightTransitLayover                       string
	OperatingAirlineDisclosure                 string
	TrafficRestrictionCode                     string
	TrafficRestrictionCodeLegOverflowIndicator string
	AircraftConfigurationVersion               string
	DateVariation                              string
	RecordSerialNumber                         uint32
	SegmentData                                []*SegmentData
}

type SegmentData struct {
	OperationalSuffix                    string
	AirlineDesignator                    string
	FlightNumber                         int
	ItineraryVariationIdentifier         int
	LegSequenceNumber                    int
	ServiceType                          string
	ItineraryVariationIdentifierOverflow string
	BoardPointIndicator                  string
	OffPointIndicator                    string
	DataElementIdentifier                string
	SegmentBoardPoint                    string
	SegmentOffPoint                      string
	Data                                 string
	RecordSerialNumber                   uint32
}

type Trailer struct {
	AirlineDesignator          string
	ReleaseSellDate            time.Time
	SerialNumberCheckReference uint32
	ContinuationEndCode        int
	RecordSerialNumber         uint32
}
