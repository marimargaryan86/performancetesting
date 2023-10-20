import lagom

from snowfall.project.junction.go.service.zendesk_webhook import amqp


def create_dependencies(
    event_producer: amqp.EventProducer,
) -> lagom.Container:
    container = lagom.Container()
    container[amqp.EventProducer] = event_producer

    return container
