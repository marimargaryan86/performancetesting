from snowfall.project.junction.go.service.offers.v1alpha import (
    models_pb2 as offer_models_pb2,
)


def parse_amenities(
    fare_feature_codes: frozenset[str],
) -> offer_models_pb2.SegmentAmenities | None:
    if fare_feature_codes:
        return offer_models_pb2.SegmentAmenities(
            beverage=_parse_amenity(fare_feature_codes, "DRIN"),
            entertainment=_parse_amenity(fare_feature_codes, "MSYS"),
            food=_parse_amenity(fare_feature_codes, "SNAC"),
            power=_parse_amenity(fare_feature_codes, "PSOC"),
            wifi=_parse_amenity(fare_feature_codes, "WIFI"),
        )

    return None


def _parse_amenity(
    fare_feature_codes: frozenset[str],
    code: str,
) -> offer_models_pb2.SegmentAmenity:
    if code in fare_feature_codes:
        availability = offer_models_pb2.SegmentAmenity.TYPE_INCLUDED
    else:
        availability = offer_models_pb2.SegmentAmenity.TYPE_UNSPECIFIED

    return offer_models_pb2.SegmentAmenity(availability=availability)
