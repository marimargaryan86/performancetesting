from snowfall.project.junction.plus.service.notifications.v1alpha import models_pb2


def proto_to_route_identifier(identifier: models_pb2.RouteIdentifier) -> str:
    return "{0}{1}".format(identifier.carrier, identifier.flight_number)
