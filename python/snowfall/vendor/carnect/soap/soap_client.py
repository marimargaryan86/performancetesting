from __future__ import annotations

import copy
import datetime
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, NamedTuple

import httpx
from xsdata.exceptions import ClientValueError
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.formats.dataclass.parsers.json import DictConverter
from xsdata.formats.dataclass.serializers import XmlSerializer

from snowfall.stdlib.logging import stdout
from snowfall.vendor.carnect.soap.log_filter import LogFilter


class Config(NamedTuple):
    """Service configuration class.

    :param style: binding style
    :param location: service endpoint url
    :param transport: transport namespace
    :param soap_action: soap action
    :param input: input object type
    :param output: output object type
    """

    style: str
    location: str
    transport: str
    soap_action: str
    input: type[Any]
    output: type[Any]

    @classmethod
    def from_service(cls, service: Any, **kwargs: Any) -> Config:
        service_params = {
            key: kwargs[key] if key in kwargs else getattr(service, key, None)
            for key in cls._fields
        }

        return cls(**service_params)


class TransportTypes(object):
    soap = "http://schemas.xmlsoap.org/soap/http"


class Singleton(type):
    _instances: ClassVar[dict[Any, Any]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SoapLogger(object):
    def __init__(
        self,
        secret_words: tuple[str, ...] | None = None,
        export_dir: Path | None = None,
        *,
        export_files: bool | None = False,
    ) -> None:
        self._logger = stdout.get_logger()
        self._log_filter = LogFilter(secret_words=secret_words)
        self._export_files = export_files
        self._operation_name_re = re.compile(r"^(.*?)(\w+)$")

        if export_dir:
            self._export_dir = export_dir
        else:
            self._export_dir = Path.cwd() / "soap_calls"

    def log(
        self,
        content_type: str,
        data_content: str | bytes | None,
        headers: Mapping[Any, Any] | None,
    ) -> None:
        operation_name = headers.get("SOAPAction", "") if headers else ""
        filtered_content = self._log_filter.log_filter(data_content)
        self._logger.info(content_type, body=filtered_content, headers=headers)
        self._export_if_needed(filtered_content, operation_name, content_type)

    def _export_if_needed(
        self,
        data_content: Any,
        operation_name: str,
        postfix: Any,
        transaction_id: Any = None,
    ) -> None:
        if not self._export_files:
            return

        self._export_dir.mkdir(exist_ok=True)

        file_name = "-".join(
            [
                datetime.datetime.now(tz=datetime.UTC).strftime(
                    "%Y-%m-%dT%H-%M-%S.%f%z",
                ),
                self._operation_name_re.sub(r"\2", operation_name),
                postfix,
            ],
        )

        if transaction_id:
            file_name = "{0}-{1}".format(file_name, transaction_id)

        file_path = (self._export_dir / file_name).with_suffix(".xml")
        file_path.write_text(data_content)


class AsyncSoapTransport(object):
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        soap_logger: SoapLogger,
        timeout: float = 2.0,
    ) -> None:
        self._timeout = timeout
        self._http_client = http_client
        self._soap_logger = soap_logger

    async def post(
        self,
        url: str,
        rq_content: str | bytes | None,
        headers: Mapping[str, str] | None,
    ) -> bytes:
        if self._soap_logger is not None:
            self._soap_logger.log("RQ", rq_content, headers)

        response = await self._http_client.post(
            url,
            content=rq_content,
            headers=headers,
            timeout=self._timeout,
        )

        rs_content = self.handle_response(response)

        if self._soap_logger is not None:
            self._soap_logger.log("RS", rs_content, headers)

        return rs_content

    @classmethod
    def handle_response(cls, response: httpx.Response) -> bytes:
        if response.status_code not in {200, 500}:
            response.raise_for_status()

        return response.content


@dataclass  # noqa: SF10
class AsyncSoapClient(object):
    config: Config
    transport: AsyncSoapTransport
    parser: XmlParser = field(default_factory=XmlParser)
    serializer: XmlSerializer = field(default_factory=XmlSerializer)
    dict_converter: DictConverter = field(init=False, default_factory=DictConverter)

    @classmethod
    def create_client(
        cls,
        service: Any,
        transport: AsyncSoapTransport,
        location: str | None,
    ) -> AsyncSoapClient:
        location = location if location else service.location
        parser = XmlParser(config=ParserConfig(fail_on_unknown_properties=False))
        client_config = Config.from_service(service, location=location)
        return AsyncSoapClient(
            config=client_config,
            transport=transport,
            parser=parser,
        )

    async def send(
        self,
        rq_object: Any,
        headers: Mapping[str, str] | None = None,
    ) -> Any:
        rq_content = self.prepare_payload(rq_object)
        headers = self.prepare_headers(headers or {})
        response = await self.transport.post(
            self.config.location,
            rq_content=rq_content,
            headers=headers,
        )
        return self.parser.from_bytes(response, self.config.output)

    def prepare_headers(self, headers: Mapping[str, str]) -> dict[str, str]:
        """Prepare request headers according to the service configuration.

        Don't mutate input headers dictionary.

        :raises ClientValueError: If the service transport type is unsupported.
        """
        res_headers = dict(copy.copy(headers))
        if self.config.transport == TransportTypes.soap:
            res_headers["content-type"] = "text/xml"
            if self.config.soap_action:
                res_headers["SOAPAction"] = self.config.soap_action
        else:
            raise ClientValueError(
                "Unsupported binding transport: `{transport}`".format(
                    transport=self.config.transport,
                ),
            )

        return res_headers

    def prepare_payload(self, rq_obj: Any) -> Any:
        """Prepare and serialize payload to be sent.

        :raises ClientValueError: If the config input type doesn't match the
            given input.
        """
        if isinstance(rq_obj, dict):
            rq_obj = self.dict_converter.convert(rq_obj, self.config.input)

        if not isinstance(rq_obj, self.config.input):
            raise ClientValueError(
                "Invalid input service type, expected `{exp}` got `{got}`".format(
                    exp=self.config.input.__name__,
                    got=type(rq_obj).__name__,
                ),
            )

        return self.serializer.render(rq_obj)
