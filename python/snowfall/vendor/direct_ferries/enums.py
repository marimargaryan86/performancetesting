import enum


class PetType(enum.Enum):
    dog = "Dog"
    cat = "Cat"
    guide_dog = "GuideDog"
    generic_pet = "GenericPet"
    dog_less_twenty_kg = "DogLess20kg"
    dog_more_twenty_kg = "DogMore20kg"
    dog_less_thirty_kg = "DogLess30kg"
    dog_more_thirty_kg = "DogMore30kg"


class SendTariffAs(enum.Enum):
    tariff_code = "TARIFFCODE"
    accommodation = "ACCOMMODATION"
    flexibility_code = "FLEXIBILITYCODE"
    onboard_facility = "ONBOARD_FACILITY"


class PassengerType(enum.Enum):
    undefined = "Undefined"
    adult = "Adult"
    child = "Child"
    infant = "Infant"
    newborn = "Newborn"
    youth = "Youth"
    student = "Student"
    senior = "Senior"
    extra_bed = "ExtraBed"
    all_types = "All"


class Gender(enum.Enum):
    male = "Male"
    female = "Female"
    unknown = "Unknown"
