import httpx


class SilverrailClient:
    def __init__(
        self,
        subscription_key: str,
        base_url: str,
        http_client: httpx.AsyncClient,
    ):
        self.subscription_key = subscription_key
