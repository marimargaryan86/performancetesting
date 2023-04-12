from twilio.rest import Client as twilioClient


class TwilioClient(object):
    def __init__(self, sid: str, token: str, sender: str):
        self._client = twilioClient(sid, token)
        self._sender = sender

    def send_message(self, receiver: str, body: str) -> None:
        self._client.messages.create(  # type: ignore[no-untyped-call]
            from_="whatsapp:{0}".format(self._sender),
            body=body,
            to="whatsapp:{0}".format("".join(receiver.split())),
        )

    def send_qr(self, receiver: str, body: str, media_url: str) -> None:
        self._client.messages.create(  # type: ignore[no-untyped-call]
            from_="whatsapp:{0}".format(self._sender),
            body=body,
            media_url=media_url,
            to="whatsapp:{0}".format("".join(receiver.split())),
        )
