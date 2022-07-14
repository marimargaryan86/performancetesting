from snowfall.vendor.direct_ferries.models import base, quote


class QuoteRequest(base.CamelCaseBaseModel):
    quote: quote.QuoteBase
