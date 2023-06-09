import lagom

from snowfall.service.geodata.v1 import geocoding_pb2_grpc
from snowfall.stdlib.integration.starlette import application


class Settings(application.Settings):
    geodata_address: str
    validate_responses_against_spec: bool = True


def create_dependencies(
    geocoding: geocoding_pb2_grpc.GeocodingServiceStub,
) -> lagom.Container:
    container = lagom.Container()
    container[geocoding_pb2_grpc.GeocodingServiceStub] = geocoding
    return container
