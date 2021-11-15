package ssim

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"strconv"
	"strings"
	"time"
)

const blockCount = 5
const blockSize = 200

type block [blockSize]byte
type blockGroup [blockCount]block

type Parser struct{}

func NewParser() *Parser {
	return &Parser{}
}

func (p *Parser) Parse(r io.Reader) (*Schedule, error) {
	scanner := bufio.NewScanner(r)
	bg, err := p.nextBlock(scanner)

	if err != nil {
		return &Schedule{}, err
	}

	s, err := p.parseSchedule(bg[0])

	if err != nil {
		return s, err
	}

	var c *Carrier
	var fl *FlightLeg
	var sd *SegmentData
	var t *Trailer

	lastSerialNumber := s.RecordSerialNumber

OuterLoop:
	for {
		bg, err = p.nextBlock(scanner)

		if err != nil {
			return s, err
		}
	InnerLoop:
		for _, b := range bg {
			switch b[0] {
			case carrierRecord:
				c, err = p.parseCarrier(b)

				if err != nil {
					return s, err
				}

				if lastSerialNumber+1 != c.RecordSerialNumber {
					return s, errors.New("invalid serial number sequence")
				}

				s.Carriers = append(s.Carriers, c)
				lastSerialNumber = c.RecordSerialNumber

				break InnerLoop
			case flightLegRecord:
				fl, err = p.parseFlightLeg(b)

				if err != nil {
					return s, err
				}

				if lastSerialNumber+1 != fl.RecordSerialNumber {
					return s, errors.New("invalid serial number sequence")
				}

				c.FlightLegs = append(c.FlightLegs, fl) // todo: records are not necessarily in order
				lastSerialNumber = fl.RecordSerialNumber
			case segmentDataRecord:
				sd, err = p.parseSegmentData(b)

				if err != nil {
					return s, err
				}

				if lastSerialNumber+1 != sd.RecordSerialNumber {
					return s, errors.New("invalid serial number sequence")
				}

				fl.SegmentData = append(fl.SegmentData, sd) // todo: records are not necessarily in order
				lastSerialNumber = sd.RecordSerialNumber
			case trailerRecord:
				t, err = p.parseTrailer(b)

				if err != nil {
					return s, err
				}

				if lastSerialNumber+1 != t.RecordSerialNumber || lastSerialNumber != t.SerialNumberCheckReference {
					return s, errors.New("invalid serial number sequence")
				}

				lastSerialNumber = t.RecordSerialNumber

				if t.ContinuationEndCode == Continuation {
					break InnerLoop
				}

				break OuterLoop
			}
		}
	}

	return s, nil
}

func (p *Parser) nextBlock(s *bufio.Scanner) (blockGroup, error) {
	var record blockGroup

	for i := 0; i < blockCount && s.Scan(); i++ {
		for k, v := range s.Bytes() {
			record[i][k] = v
		}
	}

	return record, s.Err()
}

// parseSchedule parses a block of record type 1 (header record).
//
// 1:1		Record Type				Mandatory	numeric, always 1
// 2:35		Title of Contents		Mandatory	always reads AIRLINE STANDARD SCHEDULE DATA SET
// 36:40	(Spare)					Mandatory	blank fill
// 41:41	Number of Seasons		Optional	numeric, blank fill
// 42:191	(Spare)					Mandatory	blank fill
// 192:194	Data Set Serial Number	Mandatory	numeric
// 195:200	Record Serial Number	Mandatory	numeric, always 000001
func (p *Parser) parseSchedule(b block) (*Schedule, error) {
	s := &Schedule{}

	if b[0] != headerRecord {
		return s, fmt.Errorf("record type must be '%c', '%c' parsed", headerRecord, b[0])
	}

	s.TitleOfContents = string(b[1:35])

	if s.TitleOfContents != titleOfContents {
		return s, fmt.Errorf("title of contents must be '%s', '%s' parsed", titleOfContents, s.TitleOfContents)
	}

	recordSerialNumber, err := strconv.ParseUint(string(b[194:200]), 10, 32)

	if err != nil {
		return s, err
	}

	s.RecordSerialNumber = uint32(recordSerialNumber)

	if err != nil {
		return s, err
	}

	if s.RecordSerialNumber != 1 {
		return s, fmt.Errorf("record serial number must be '1', '%d' parsed", s.RecordSerialNumber)
	}

	dataSetSerialNumber, err := strconv.ParseUint(string(b[191:194]), 10, 16)

	if err != nil {
		return s, err
	}

	s.DataSetSerialNumber = uint16(dataSetSerialNumber)
	numOfSeasons := strings.TrimSpace(string(b[40]))

	if numOfSeasons != "" {
		numOfSeasonsInt, err := strconv.ParseUint(numOfSeasons, 10, 8)

		if err != nil {
			return s, err
		}

		s.NumberOfSeasons = uint8(numOfSeasonsInt)
	}

	s.Carriers = make([]*Carrier, 0)

	return s, nil
}

// parseCarrier parses a block of record type 2 (carrier record).
//
// 1:1		Record Type							Mandatory	numeric, always 2
// 2:2		Time Mode							Mandatory 	either U (UTC) or L (Local Time)
// 3:5		Airline Designator					Mandatory	IATA or ICAO code, left justify
// 6:10		(Spare)								Mandatory	blank fill
// 11:13	Season								Optional	Syy or Wyy, blank fill
// 14:14	(Spare)								Mandatory
// 15:28	Period of Schedule Validity			Mandatory	e.g. 28MAR0130OCT01
// 29:35	Creation Date						Mandatory	e.g. 01APR90
// 36:64	Title of Data						Optional	free format, blank fill
// 65:71	Release (Sell) Date					Optional	e.g. 14MAR01, or blank fill
// 72:72	Schedule Status						Mandatory	either P (Provisional) or C (Confirmed)
// 73:107	Creator Reference					Optional	free format, blank fill
// 108:108	Duplicate Airline Designator Marker	Conditional	blank fill
// 109:169	General Information					Optional	free format, blank fill
// 170:188	In-Flight Service Information		Optional	right justified, blank fill
// 189:190	Electronic Ticketing Information	Optional	either EN (Not Electronic Ticketing Candidate) or ET (Electronic Ticketing Candidate)
// 191:194	Creation Time						Mandatory	e.g. 1346
// 195:200	Record Serial Number				Mandatory	numeric, zero fill, right justified
func (p *Parser) parseCarrier(b block) (*Carrier, error) {
	var err error

	c := &Carrier{}

	if b[0] != carrierRecord {
		return c, fmt.Errorf("record type must be '%c', '%c' parsed", carrierRecord, b[0])
	}

	switch b[1] {
	case 'L':
		c.TimeMode = Local
	case 'U':
		c.TimeMode = Utc
	default:
		return c, fmt.Errorf("time mode must be either 'L' or 'U', '%c' parsed", b[1])
	}

	c.AirlineDesignator = strings.TrimSpace(string(b[2:5]))
	season := strings.TrimSpace(string(b[10:13]))

	if season != "" {
		c.Season = season
	}

	if string(b[14:21]) != "00XXX00" {
		from, err := time.Parse("02Jan06", string(b[14:21]))

		if err != nil {
			return c, err
		}

		c.ScheduleValidFrom = from
	}

	if string(b[21:28]) != "00XXX00" {
		to, err := time.Parse("02Jan06", string(b[21:28]))

		if err != nil {
			return c, err
		}

		c.ScheduleValidTo = to
	}

	creationDate := strings.TrimSpace(string(b[28:35]) + string(b[190:194]))

	if creationDate != "" {
		c.CreationDate, err = time.Parse("02Jan061504", creationDate)

		if err != nil {
			return c, err
		}
	}

	c.TitleOfData = strings.TrimSpace(string(b[35:64]))
	releaseSellDate := strings.TrimSpace(string(b[28:35]))

	if releaseSellDate != "" {
		c.ReleaseSellDate, err = time.Parse("02Jan06", releaseSellDate)

		if err != nil {
			return c, err
		}
	}

	switch b[71] {
	case 'C':
		c.ScheduleStatus = Confirmed
	case 'P':
		c.ScheduleStatus = Provisional
	default:
		return c, fmt.Errorf("schedule status must be either 'C' or 'P', '%c' parsed", b[71])
	}

	c.CreatorReference = strings.TrimSpace(string(b[72:107]))

	if strings.TrimSpace(string(b[107])) != "" {
		c.DuplicateAirlineDesignator = true
	}

	c.GeneralInformation = strings.TrimSpace(string(b[108:168]))
	// @todo: secure flight indicator missing
	c.InFlightServiceInformation = strings.TrimSpace(string(b[169:188]))
	c.ElectronicTicketingInformation = strings.TrimSpace(string(b[188:190]))
	recordSerialNumber, err := strconv.ParseUint(string(b[194:200]), 10, 32)

	if err != nil {
		return c, err
	}

	c.RecordSerialNumber = uint32(recordSerialNumber)

	c.FlightLegs = make([]*FlightLeg, 0)

	return c, err
}

// parseFlightLeg parses a block of record type 3 (flight leg record).
//
// 1:1		Record Type										Mandatory	numeric, always 3
// 2:2		Operational Suffix								Conditional	blank fill
// 3:5		Airline Designator								Mandatory	IATA or ICAO code, left justified
// 6:9		Flight Number									Mandatory	right justified, blank fill
// 10:11	Itinerary Variation Identifier					Mandatory	number between 01 and 99
// 12:13	Leg Sequence Number								Mandatory   number between 01 and 99
// 14:14	Service Type									Mandatory	alpha
// 15:28	Period of Operation								Mandatory	e.g. 28MAR0130OCT01
// 29:35	Day(s) of Operation								Mandatory	blank filled for non-operational days
// 36:36	Frequency Rate									Conditional	blank fill
// 37:39	Departure Station								Mandatory	3-character IATA code
// 40:43	Scheduled Time of Passenger Departure			Mandatory
// 44:47	Scheduled Time of Aircraft Departure			Mandatory
// 48:52	UTC/Local Time Variation (Departure)			Mandatory	hours and minutes variation from UTC
// 53:54	Passenger Terminal (Departure)					Conditional	alphanumeric, left justify, blank fill
// 55:57	Arrival Station									Mandatory	3-character IATA code
// 58:61	Scheduled Time of Aircraft Arrival				Mandatory
// 62:65	Scheduled Time of Passenger Arrival				Mandatory
// 66:70	UTC/Local Time Variation (Arrival)				Mandatory	hours and minutes variation from UTC
// 71:72	Passenger Terminal (Arrival)					Conditional	alphanumeric, left justify, blank fill
// 73:75	Aircraft Type									Mandatory	ATA/IATA aircraft type
// 76:95	Passenger Reservations Booking Designator		Conditional	blank fill
// 96:100	Passenger Reservations Booking Modifier			Conditional	blank fill by passenger reservations booking designator class
// 101:110 	Meal Service Note								Optional	blank fill by passenger reservations booking designator class
// 111:119	Joint Operation Airline Designators				Conditional	left justify and blank fill if fewer than three carriers
// 120:121	Minimum Connection Time Status					Optional	blank fill, two character combination of D and/or I
// 122:122	Secure Flight Indicator							Optional	blank fill, S if subject to regulations
// 123:127	(Spare)											Mandatory	blank fill
// 128:128	Itinerary Variation Identifier Overflow			Conditional	blank fill
// 129:131	Aircraft Owner									Conditional left justify, blank fill
// 132:134	Cockpit Crew Employer							Conditional	left justify, blank fill
// 135:137	Cabin Crew Employer								Conditional left justify, blank fill
// 138:146	Onward Flight									Optional	blank fill
// 138:140	- Airline Designator							Mandatory	left justify, blank fill
// 141:144	- Flight Number									Mandatory	right justify, blank fill
// 145:145	- Aircraft Rotation Layover						Conditional	blank fill
// 146:146	- Operational Suffix							Conditional	blank fill
// 147:147	(Spare)											Mandatory	blank fill
// 148:148	Flight Transit Layover							Conditional	blank fill
// 149:149	Operating Airline Disclosure					Conditional	blank fill
// 150:160	Traffic Restriction Code						Conditional blank fill
// 161:161	Traffic Restriction Code Leg Overflow Indicator	Conditional	blank fill
// 162:172	(Spare)											Mandatory	blank fill
// 173:192	Aircraft Configuration/Version					Conditional	blank fill
// 193:194	Date Variation									Optional	blank fill
// 195:200	Record Serial Number							Mandatory	numeric, zero fill, right justified
func (p *Parser) parseFlightLeg(b block) (*FlightLeg, error) {
	fl := &FlightLeg{}

	if b[0] != flightLegRecord {
		return fl, fmt.Errorf("record type must be '%c', '%c' parsed", flightLegRecord, b[0])
	}

	var err error

	fl.OperationalSuffix = strings.TrimSpace(string(b[1]))
	fl.AirlineDesignator = strings.TrimSpace(string(b[2:5]))
	fl.FlightNumber, err = strconv.Atoi(strings.TrimSpace(string(b[5:9])))

	if err != nil {
		return fl, fmt.Errorf("unable to convert flight number: %w", err)
	}

	fl.ItineraryVariationIdentifier, err = strconv.Atoi(string(b[9:11]))

	if err != nil {
		return fl, fmt.Errorf("unable to convert itinerary variation identifier: %w", err)
	}

	fl.LegSequenceNumber, err = strconv.Atoi(string(b[11:13]))

	if err != nil {
		return fl, fmt.Errorf("unable to convert leg sequence number: %w", err)
	}

	fl.ServiceType = string(b[13])

	if string(b[14:21]) != "00XXX00" { // @todo: handle better
		fl.PeriodOfOperationFrom, err = time.Parse("02Jan06", string(b[14:21]))

		if err != nil {
			return fl, err
		}
	}

	if string(b[21:28]) != "00XXX00" { // @todo: handle better
		fl.PeriodOfOperationTo, err = time.Parse("02Jan06", string(b[21:28]))

		if err != nil {
			return fl, err
		}
	}

	fl.DaysOfOperation = string(b[28:35])

	if b[35] != ' ' {
		fl.FrequencyRate, err = strconv.Atoi(string(b[35]))

		if err != nil {
			return fl, fmt.Errorf("unable to convert frequencey rate: %w", err)
		}
	} else {
		fl.FrequencyRate = 1
	}

	fl.DepartureStation = string(b[36:39])
	fl.ScheduledTimeOfPassengerDeparture, err = time.ParseDuration(fmt.Sprintf("%sh%sm", string(b[39:41]), string(b[41:43])))

	if err != nil {
		return fl, err
	}

	fl.ScheduledTimeOfAircraftDeparture, err = time.ParseDuration(fmt.Sprintf("%sh%sm", string(b[43:45]), string(b[45:47])))

	if err != nil {
		return fl, err
	}

	fl.UtcLocalTimeVariationDepartureStation = string(b[47:52])
	fl.PassengerTerminalDepartureStation = string(b[52:54])
	fl.ArrivalStation = string(b[54:57])
	fl.ScheduledTimeOfAircraftArrival, err = time.ParseDuration(fmt.Sprintf("%sh%sm", string(b[57:59]), string(b[59:61])))

	if err != nil {
		return fl, err
	}

	fl.ScheduledTimeOfPassengerArrival, err = time.ParseDuration(fmt.Sprintf("%sh%sm", string(b[61:63]), string(b[63:65])))

	if err != nil {
		return fl, err
	}

	fl.UtcLocalTimeVariationArrivalStation = string(b[65:70])
	fl.PassengerTerminalArrivalStation = string(b[70:72])
	fl.AircraftType = string(b[72:75])
	fl.PassengerReservationsBookingDesignator = string(b[75:95])
	fl.PassengerReservationsBookingModifier = string(b[95:100])
	fl.MealServiceNote = string(b[100:110])
	fl.JointOperationAirlineDesignators = string(b[110:119])
	fl.MinimumConnectingTimeStatus = string(b[119:121])
	fl.SecureFlightIndicator = string(b[121])
	fl.ItineraryVariationIdentifierOverflow = string(b[127])
	fl.AircraftOwner = string(b[128:131])
	fl.CockpitCrewEmployer = string(b[131:134])
	fl.CabinCrewEmployer = string(b[134:137])

	if strings.TrimSpace(string(b[137:146])) != "" {
		fl.OnwardFlightAirlineDesignator = string(b[137:140])
		fl.OnwardFlightFlightNumber, err = strconv.Atoi(strings.TrimSpace(string(b[140:144])))

		if err != nil {
			return fl, err
		}

		fl.OnwardFlightAircraftRotationLayover = string(b[144])
		fl.OnwardFlightOperationalSuffix = strings.TrimSpace(string(b[145]))
	}

	fl.FlightTransitLayover = string(b[147])
	fl.OperatingAirlineDisclosure = string(b[148])
	fl.TrafficRestrictionCode = string(b[149:160])
	fl.TrafficRestrictionCodeLegOverflowIndicator = string(b[160])
	fl.AircraftConfigurationVersion = string(b[172:192])
	fl.DateVariation = string(b[192:194])
	recordSerialNumber, err := strconv.ParseUint(string(b[194:200]), 10, 32)

	if err != nil {
		return fl, err
	}

	fl.RecordSerialNumber = uint32(recordSerialNumber)
	fl.SegmentData = make([]*SegmentData, 0)

	return fl, nil
}

func (p *Parser) parseSegmentData(b block) (*SegmentData, error) {
	sd := &SegmentData{}

	if b[0] != segmentDataRecord {
		return sd, fmt.Errorf("record type must be '%c', '%c' parsed", segmentDataRecord, b[0])
	}

	var err error

	sd.OperationalSuffix = string(b[1])
	sd.AirlineDesignator = string(b[2:5])
	sd.FlightNumber, err = strconv.Atoi(strings.TrimSpace(string(b[5:9])))

	if err != nil {
		return sd, fmt.Errorf("unable to convert flight number: %w", err)
	}

	sd.ItineraryVariationIdentifier, err = strconv.Atoi(string(b[9:11]))

	if err != nil {
		return sd, fmt.Errorf("unable to convert itinerary variation identifier: %w", err)
	}

	sd.LegSequenceNumber, err = strconv.Atoi(string(b[11:13]))

	if err != nil {
		return sd, fmt.Errorf("unable to convert leg sequence number: %w", err)
	}

	sd.ServiceType = string(b[13])
	sd.ItineraryVariationIdentifierOverflow = string(b[27])
	sd.BoardPointIndicator = string(b[28])
	sd.OffPointIndicator = string(b[29])
	sd.DataElementIdentifier = string(b[30:33])
	sd.SegmentBoardPoint = string(b[33:36])
	sd.SegmentOffPoint = string(b[36:39])
	sd.Data = string(b[39:194])
	recordSerialNumber, err := strconv.ParseUint(string(b[194:200]), 10, 32)

	if err != nil {
		return sd, err
	}

	sd.RecordSerialNumber = uint32(recordSerialNumber)

	return sd, nil
}

func (p *Parser) parseTrailer(b block) (*Trailer, error) {
	t := &Trailer{}

	if b[0] != trailerRecord {
		return t, fmt.Errorf("record type must be '%c', '%c' parsed", trailerRecord, b[0])
	}

	t.AirlineDesignator = string(b[2:5])
	releaseSellDate := strings.TrimSpace(string(b[28:35]))

	var err error

	if releaseSellDate != "" {
		t.ReleaseSellDate, err = time.Parse("02Jan06", releaseSellDate)

		if err != nil {
			return t, err
		}
	}

	serialNumberCheckReference, err := strconv.ParseUint(string(b[187:193]), 10, 32)

	if err != nil {
		return t, err
	}

	t.SerialNumberCheckReference = uint32(serialNumberCheckReference)

	switch b[193] {
	case 'C':
		t.ContinuationEndCode = Continuation
	case 'E':
		t.ContinuationEndCode = End
	default:
		return t, fmt.Errorf("continuation/end code must be either 'C' or 'E', '%c' parsed", b[193])
	}

	recordSerialNumber, err := strconv.ParseUint(string(b[194:200]), 10, 32)

	if err != nil {
		return t, err
	}

	t.RecordSerialNumber = uint32(recordSerialNumber)

	return t, nil
}
