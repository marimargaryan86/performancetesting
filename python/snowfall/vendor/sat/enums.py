from enum import Enum


class TripType(Enum):
    one_way = 1
    round_trip = 2


class PassengerType(Enum):
    adult = "Adult"
    senior = "Senior"
    youth = "Youth"
