from google.protobuf import message

from snowfall.project.junction.provider import meta, service
from snowfall.project.junction.service.providers.karhoo import (
    config,
    offers,
    orders,
    pricing,
    simple_offers,
)
from snowfall.project.junction.service.providers.karhoo.constant import PROVIDER_ID
from snowfall.project.junction.service.providers.karhoo.v1 import amqp_pb2

_PROVIDER_NAME = "Karhoo"


async def _meta_factory() -> meta.MetaImplementation:
    return meta.MetaImplementation(identifier=PROVIDER_ID, name=_PROVIDER_NAME)


if __name__ == "__main__":
    entrypoint: service.Entrypoint[
        config.Settings,
        message.Message,
        amqp_pb2.Criteria,
    ] = service.Entrypoint(
        name="karhoo",
        simple_offers_factory=simple_offers.simple_search_app,
        meta_factory=_meta_factory,
        settings_class=config.Settings,
    )
    entrypoint.enter_with_commands(
        service.Command(
            name="offers",
            callback=offers.offers,
            settings_class=config.OfferSettings,
        ),
        service.Command(
            name="pricing",
            callback=pricing.price_quotes,
            settings_class=config.OfferSettings,
        ),
        service.Command(
            name="orders",
            callback=orders.orders,
            settings_class=config.OrderSettings,
        ),
    )
