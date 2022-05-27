from enum import Enum


class TripType(Enum):
    one_way = 1
    round_trip = 2


class PassengerType(Enum):
    adult = "Adult"
    senior = "Senior"
    youth = "Youth"


class PassengerTitle(Enum):
    mr = "Mr"
    mrs = "Mrs"
    miss = "Miss"
    ms = "Ms"


class PassengerGender(Enum):
    male = "M"
    female = "F"
