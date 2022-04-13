package ssim

import (
	"bufio"
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

type Result struct {
	Record interface{}
	Error  error
}

type Parser struct{}

func NewParser() *Parser {
	return &Parser{}
}

func (p *Parser) Parse(r io.Reader) chan Result {
	ch := make(chan Result)

	go func() {
		var s Schedule
		var c Carrier
		var fl FlightLeg
		var sd SegmentData
		var t Trailer

		defer close(ch)

		lastSerialNumber := uint32(0)
		scanner := bufio.NewScanner(r)

	OuterLoop:
		for {
			bg, err := p.nextBlock(scanner)

			if err != nil {
				ch <- Result{s, err}
				break
			}
		InnerLoop:
			for _, b := range bg {
				if lastSerialNumber == 999999 {
					lastSerialNumber = 1
				}

				switch b[0] {
				case headerRecord:
					s, err = p.parseSchedule(bg[0])

					if err != nil {
						ch <- Result{s, err}
						break OuterLoop
					}

					if lastSerialNumber+1 != s.RecordSerialNumber {
						ch <- Result{s, fmt.Errorf("invalid serial number sequence, expected %d got %d", lastSerialNumber+1, s.RecordSerialNumber)}
						break OuterLoop
					}

					lastSerialNumber = s.RecordSerialNumber

					ch <- Result{s, nil}

					break InnerLoop
				case carrierRecord:
					c, err = p.parseCarrier(b)

					if err != nil {
						ch <- Result{c, err}
						break OuterLoop
					}

					if lastSerialNumber+1 != c.RecordSerialNumber {
						ch <- Result{c, fmt.Errorf("invalid serial number sequence, expected %d got %d", lastSerialNumber+1, c.RecordSerialNumber)}
						break OuterLoop
					}

					lastSerialNumber = c.RecordSerialNumber

					ch <- Result{c, nil}

					break InnerLoop
				case flightLegRecord:
					fl, err = p.parseFlightLeg(b)

					if err != nil {
						ch <- Result{fl, err}
						break OuterLoop
					}

					if lastSerialNumber+1 != fl.RecordSerialNumber {
						ch <- Result{fl, fmt.Errorf("invalid serial number sequence, expected %d got %d", lastSerialNumber+1, fl.RecordSerialNumber)}
						break OuterLoop
					}

					lastSerialNumber = fl.RecordSerialNumber

					if fl.PeriodOfOperationTo.IsZero() {
						if c.ScheduleValidTo.IsZero() {
							fl.PeriodOfOperationTo = time.Date(
								c.ScheduleValidFrom.Year()+1,
								c.ScheduleValidFrom.Month(),
								c.ScheduleValidFrom.Day()-1,
								c.ScheduleValidFrom.Hour(),
								c.ScheduleValidFrom.Minute(),
								c.ScheduleValidFrom.Second(),
								c.ScheduleValidFrom.Nanosecond(),
								c.ScheduleValidFrom.Location(),
							)
						} else {
							fl.PeriodOfOperationTo = c.ScheduleValidTo
						}
					}

					ch <- Result{fl, nil}
				case segmentDataRecord:
					sd, err = p.parseSegmentData(b)

					if err != nil {
						ch <- Result{sd, err}
						break OuterLoop
					}

					if lastSerialNumber+1 != sd.RecordSerialNumber {
						ch <- Result{sd, fmt.Errorf("invalid serial number sequence, expected %d got %d", lastSerialNumber+1, sd.RecordSerialNumber)}
						break OuterLoop
					}

					lastSerialNumber = sd.RecordSerialNumber

					ch <- Result{sd, nil}
				case trailerRecord:
					t, err = p.parseTrailer(b)

					if err != nil {
						ch <- Result{t, err}
						break OuterLoop
					}

					if lastSerialNumber+1 != t.RecordSerialNumber {
						ch <- Result{t, fmt.Errorf("invalid serial number sequence, expected %d got %d", lastSerialNumber+1, t.RecordSerialNumber)}
						break OuterLoop
					}

					if lastSerialNumber != t.SerialNumberCheckReference {
						ch <- Result{t, fmt.Errorf("invalid serial number check reference, expected %d got %d", lastSerialNumber, t.SerialNumberCheckReference)}
						break OuterLoop
					}

					lastSerialNumber = t.RecordSerialNumber

					ch <- Result{t, nil}

					if t.ContinuationEndCode == Continuation {
						break InnerLoop
					}

					break OuterLoop
				}
			}
		}
	}()

	return ch
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
func (p *Parser) parseSchedule(b block) (Schedule, error) {
	s := Schedule{}

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

	return s, nil
}

// parseCarrier parses a block of record type 2 (carrier record).
func (p *Parser) parseCarrier(b block) (Carrier, error) {
	var err error

	c := Carrier{}

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

	return c, err
}

// parseFlightLeg parses a block of record type 3 (flight leg record).
func (p *Parser) parseFlightLeg(b block) (FlightLeg, error) {
	fl := FlightLeg{}

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

	if string(b[127]) == " " {
		fl.ItineraryVariationIdentifierOverflow = 0
	} else {
		fl.ItineraryVariationIdentifierOverflow, err = strconv.Atoi(string(b[127]))

		if err != nil {
			return fl, fmt.Errorf("unable to convert itinerary variation identifier overflow: %w", err)
		}
	}

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

	return fl, nil
}

func (p *Parser) parseSegmentData(b block) (SegmentData, error) {
	sd := SegmentData{}

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

func (p *Parser) parseTrailer(b block) (Trailer, error) {
	t := Trailer{}

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
