from collections.abc import Sequence

from pydantic import v1 as pyd

from snowfall.vendor.direct_ferries.models.quote import Quote as VendorQuote


class Quote(pyd.BaseModel):
    quote: VendorQuote
    round_trip_offer_cache_keys: Sequence[str] = []
    redis_key: str | None
