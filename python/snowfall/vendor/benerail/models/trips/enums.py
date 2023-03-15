from enum import Enum


class TripErrorCodes(Enum):
    trip_not_found = "trip.not.found"
    trip_collection_not_found = "trip.collection.not.found"
    origin_not_found = "origin.not.found"
    destination_not_found = "destination.not.found"
    train_type_not_found = "train.type.not.found"
