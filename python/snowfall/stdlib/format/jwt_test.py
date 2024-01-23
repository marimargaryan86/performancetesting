import base64
import datetime

import jwt as jwtlib
import pytest
import pytest_httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from snowfall.stdlib.format import jwt


@pytest.fixture()
def raw_private_key() -> ed25519.Ed25519PrivateKey:
    return ed25519.Ed25519PrivateKey.generate()


@pytest.fixture()
def private_key(raw_private_key: ed25519.Ed25519PrivateKey) -> str:
    return base64.b64encode(
        raw_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    ).decode()


@pytest.fixture()
def public_key(raw_private_key: ed25519.Ed25519PrivateKey) -> str:
    return base64.b64encode(
        raw_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ),
    ).decode()


@pytest.fixture()
def unencrypted_payload() -> str:
    return jwt.Encoder().encode(jwt.Payload())


@pytest.fixture()
def encoder(private_key: str) -> jwt.Encoder:
    return jwt.Encoder(private_key=private_key, algorithm="EdDSA")


@pytest.fixture()
def encrypted_payload(encoder: jwt.Encoder) -> str:
    return encoder.encode(jwt.Payload())


class TestEncoder(object):
    def test_payload_is_encoded(self) -> None:
        encoder = jwt.Encoder()
        encoded = encoder.encode(jwt.Payload())
        assert jwtlib.decode(encoded, options={"verify_signature": False})

    def test_jwt_contains_custom_dict(self) -> None:
        encoder = jwt.Encoder()
        encoded = encoder.encode(jwt.Payload())
        decoded = jwtlib.decode(encoded, options={"verify_signature": False})
        assert isinstance(decoded.get("custom"), dict)

    def test_empty_private_key_can_encode(self) -> None:
        encoder = jwt.Encoder()
        assert encoder.encode(jwt.Payload())

    def test_private_key_can_encode(self, private_key: str) -> None:
        encoder = jwt.Encoder(private_key=private_key, algorithm="EdDSA")
        assert encoder.encode(jwt.Payload())

    def test_faulty_algorithm_raises_error(self, private_key: str) -> None:
        with pytest.raises(TypeError, match="Ed25519PrivateKey.sign"):
            jwt.Encoder(private_key=private_key, algorithm="RS256")

    def test_faulty_key_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Unable to load PEM file"):
            jwt.Encoder(private_key="Zm9v", algorithm="RS256")


class TestDecoder(object):
    def test_unencrypted_payload_can_be_decoded(self, unencrypted_payload: str) -> None:
        decoder = jwt.Decoder()
        assert decoder.decode(unencrypted_payload)

    def test_encrypted_key_can_be_decoded(
        self,
        public_key: str,
        encrypted_payload: str,
    ) -> None:
        decoder = jwt.Decoder(public_key=public_key, algorithms=["EdDSA"])
        assert decoder.decode(encrypted_payload)


_JWK_URL = "http://localhost/.well-known/jwks.json"


@pytest.fixture()
def jwk_client(
    public_key: str,
    httpx_mock: pytest_httpx.HTTPXMock,
) -> jwt.AsyncJWKClient:
    fake_jwks = {
        "keys": [
            {
                "use": "sig",
                "kty": "RSA",
                "kid": "foobar",
                "alg": "RS256",
                "n": public_key,
                "e": "AQAB",
            },
        ],
    }
    httpx_mock.add_response(
        url=_JWK_URL,
        json=fake_jwks,
    )

    return jwt.AsyncJWKClient(
        jwk_url=_JWK_URL,
        key_ttl=datetime.timedelta(hours=1),
    )


@pytest.fixture()
def assert_all_responses_were_requested() -> bool:
    return False


@pytest.fixture()
def payload_with_kid(encoder: jwt.Encoder) -> str:
    return encoder.encode(jwt.Payload(), headers={"kid": "foobar"})


@pytest.fixture()
def payload_with_unknown_kid(encoder: jwt.Encoder) -> str:
    return encoder.encode(jwt.Payload(), headers={"kid": "bazqux"})


class TestJWKClient(object):
    async def test_signing_keys_are_fetched_once(
        self,
        jwk_client: jwt.AsyncJWKClient,
        payload_with_kid: str,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        await jwk_client.get_signing_key_from_jwt(payload_with_kid)
        await jwk_client.get_signing_key_from_jwt(payload_with_kid)
        assert len(httpx_mock.get_requests()) == 1

    async def test_signing_keys_are_fetched_again_with_unknown_kid(
        self,
        jwk_client: jwt.AsyncJWKClient,
        payload_with_unknown_kid: str,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        with pytest.raises(jwtlib.PyJWKClientError):
            await jwk_client.get_signing_key_from_jwt(payload_with_unknown_kid)

        with pytest.raises(jwtlib.PyJWKClientError):
            await jwk_client.get_signing_key_from_jwt(payload_with_unknown_kid)

        assert len(httpx_mock.get_requests()) == 3

    async def test_signing_keys_are_not_fetched_again_with_no_kid(
        self,
        jwk_client: jwt.AsyncJWKClient,
        encrypted_payload: str,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        with pytest.raises(jwtlib.PyJWKError):
            await jwk_client.get_signing_key_from_jwt(encrypted_payload)

        with pytest.raises(jwtlib.PyJWKError):
            await jwk_client.get_signing_key_from_jwt(encrypted_payload)

        assert not len(httpx_mock.get_requests())
