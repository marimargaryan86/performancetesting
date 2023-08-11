import pydantic


class EtagData(pydantic.BaseModel):
    dialogue_etag: str = ""
    booking_etag: str = ""
    offer_etag: str = ""
    trip_offers_etag: str = ""
    trip_offer_collection_etag: str = ""
    payment_etag: str = ""
    selected_offer_etag: str = ""
    order_etag: str = ""
    fulfillments_etag: str = ""
    passenger_etags: dict[str, str] = pydantic.Field(default_factory=dict)
