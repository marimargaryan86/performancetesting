from __future__ import annotations

import abc
import dataclasses
from collections.abc import Iterator
from typing import Optional, Sequence

import grpc

from snowfall.project.junction.adapter import errors
from snowfall.project.junction.service.offers.v1alpha import (
    grpc_pb2,
    grpc_pb2_grpc,
    models_pb2,
)
from snowfall.stdlib import sequence
from snowfall.stdlib.v1alpha import models_pb2 as common_pb2


class NotFoundError(Exception):
    """Raised when an offer is not found."""


class UnknownError(Exception):
    """Raised when an unhandled error occurs."""


@dataclasses.dataclass(frozen=True)
class OffersPage(object):
    offers: Sequence[models_pb2.OfferAggregate]
    next_page_token: str = ""

    @classmethod
    def from_proto(cls, grpc_offers: grpc_pb2.ListOffersResponse) -> OffersPage:
        return cls(
            offers=grpc_offers.offers,
            next_page_token=grpc_offers.next_page_token,
        )


class Client(abc.ABC):  # noqa: WPS214
    @abc.abstractmethod
    async def get(self, identifier: str) -> models_pb2.OfferAggregate:
        """Fetch an offer resource."""

    @abc.abstractmethod
    async def find_offers_by_offer_search(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        cabin_classes: Optional[Sequence[common_pb2.CabinClass.Type.ValueType]] = None,
    ) -> OffersPage:
        """Get offer results for an offer search."""

    @abc.abstractmethod
    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OffersPage:
        """Return offers by offer ids."""

    @abc.abstractmethod
    async def get_group_by_id(self, identifier: str) -> models_pb2.OfferGroup:
        """Return offer group by id."""

    @abc.abstractmethod
    async def find_groups_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferGroupsResponse:
        """Return offer groups by ids."""

    @abc.abstractmethod
    async def get_group_details_by_id(self, identifier: str) -> models_pb2.OfferSegment:
        """Return offer group details by id."""

    @abc.abstractmethod
    async def find_group_details_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferGroupDetailsResponse:
        """Return offer group details by ids."""

    @abc.abstractmethod
    async def get_option_by_id(self, identifier: str) -> models_pb2.Offer:
        """Return offer option by id."""

    @abc.abstractmethod
    async def find_options_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferOptionsResponse:
        """Return offers by ids."""

    @abc.abstractmethod
    async def get_option_details_by_id(
        self,
        identifier: str,
    ) -> models_pb2.OfferSegmentDetails:
        """Return offer option details by id."""

    @abc.abstractmethod
    async def find_option_details_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferOptionDetailsResponse:
        """Return offer details by ids."""


class DictClient(Client):  # noqa: WPS214
    def __init__(self, offers: Sequence[models_pb2.OfferAggregate]) -> None:
        self._offers: dict[str, models_pb2.OfferAggregate] = {
            offer.id: offer for offer in offers
        }

    async def get(self, offer_id: str) -> models_pb2.OfferAggregate:
        if offer_id not in self._offers:
            raise NotFoundError()

        return self._offers[offer_id]

    async def find_offers_by_offer_search(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        cabin_classes: Optional[Sequence[common_pb2.CabinClass.Type.ValueType]] = None,
    ) -> OffersPage:
        offers = [
            offer
            for offer in self._offers.values()
            if offer.groups and offer.groups[0].offer_search_id == identifier
        ]

        if cabin_classes:
            offers = [
                offer
                for offer in offers
                if self._offer_has_cabin_classes(offer, cabin_classes)
            ]

        page = sequence.paginate(
            sequence=offers,
            cursor=cursor,
            limit=limit,
        )

        return OffersPage(
            offers=page.sequence,
            next_page_token=page.cursor,
        )

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OffersPage:
        page = sequence.paginate(
            sequence=[
                self._offers[identifier]
                for identifier in identifiers
                if identifier in self._offers
            ],
            cursor=cursor,
            limit=limit,
        )

        return OffersPage(
            offers=page.sequence,
            next_page_token=page.cursor,
        )

    async def get_group_by_id(self, identifier: str) -> models_pb2.OfferGroup:
        for group in self._iterate_groups():
            if group.id == identifier:
                return group

        raise NotFoundError()

    async def find_groups_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferGroupsResponse:
        page = sequence.paginate(
            sequence=list(self._iterate_groups()),
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListOfferGroupsResponse(
            groups=page.sequence,
            next_page_token=page.cursor,
        )

    async def get_group_details_by_id(self, identifier: str) -> models_pb2.OfferSegment:
        for group in self._iterate_groups():
            for detail in group.segments:
                if detail.id == identifier:
                    return detail

        raise NotFoundError()

    async def find_group_details_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferGroupDetailsResponse:
        page = sequence.paginate(
            sequence=[
                detail for group in self._iterate_groups() for detail in group.segments
            ],
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListOfferGroupDetailsResponse(
            details=page.sequence,
            next_page_token=page.cursor,
        )

    async def get_option_by_id(self, identifier: str) -> models_pb2.Offer:
        for option in self._iterate_options():
            if option.id == identifier:
                return option

        raise NotFoundError()

    async def find_options_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferOptionsResponse:
        page = sequence.paginate(
            sequence=list(self._iterate_options()),
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListOfferOptionsResponse(
            options=page.sequence,
            next_page_token=page.cursor,
        )

    async def get_option_details_by_id(
        self,
        identifier: str,
    ) -> models_pb2.OfferSegmentDetails:
        for option in self._iterate_options():
            for details in option.segment_details:
                if details.id == identifier:
                    return details

        raise NotFoundError()

    async def find_option_details_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferOptionDetailsResponse:
        page = sequence.paginate(
            sequence=[
                detail
                for option in self._iterate_options()
                for detail in option.segment_details
            ],
            cursor=cursor,
            limit=limit,
        )

        return grpc_pb2.ListOfferOptionDetailsResponse(
            details=page.sequence,
            next_page_token=page.cursor,
        )

    def _iterate_groups(self) -> Iterator[models_pb2.OfferGroup]:
        for offer in self._offers.values():
            yield from offer.groups

    def _iterate_options(self) -> Iterator[models_pb2.Offer]:
        for group in self._iterate_groups():
            yield from group.offers

    def _offer_has_cabin_classes(
        self,
        offer: models_pb2.OfferAggregate,
        cabin_classes: Sequence[common_pb2.CabinClass.Type.ValueType],
    ) -> bool:
        options = [option for group in offer.groups for option in group.offers]

        return any(
            detail.cabin_class.type in cabin_classes
            for option in options
            for detail in option.segment_details
        )


class GrpcClient(Client):  # noqa: WPS214
    def __init__(self, offers: grpc_pb2_grpc.OfferServiceStub, timeout: int = 10):
        self._offers = offers
        self._timeout = timeout

    async def get(self, offer_id: str) -> models_pb2.OfferAggregate:
        try:
            response = await self._offers.GetOffer(
                grpc_pb2.GetOfferRequest(id=offer_id),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Offer with ID '{id}' not found.".format(id=offer_id),
                ) from exc

            raise UnknownError() from exc

        return response.offer

    async def find_offers_by_offer_search(
        self,
        identifier: str,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        cabin_classes: Optional[Sequence[common_pb2.CabinClass.Type.ValueType]] = None,
    ) -> OffersPage:
        request = grpc_pb2.ListOffersRequest(
            page_token=cursor or "",
            offer_search_id=identifier,
            cabin_class_types=cabin_classes,
        )
        if limit is not None:
            request.page_size = limit

        try:
            response = await errors.handle_grpc_errors(
                self._offers.ListOffers(request, timeout=self._timeout),
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError(exc.details()) from exc

        return OffersPage(
            offers=response.offers,
            next_page_token=response.next_page_token,
        )

    async def find_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OffersPage:
        request = grpc_pb2.ListOffersRequest(
            page_token=cursor or "",
            offer_ids=grpc_pb2.ListOfIds(ids=list(identifiers)),
        )

        if limit is not None:
            request.page_size = limit

        try:
            response = await errors.handle_grpc_errors(
                self._offers.ListOffers(request, timeout=self._timeout),
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError() from exc

        return OffersPage(
            offers=list(response.offers),
            next_page_token=response.next_page_token,
        )

    async def get_group_by_id(self, identifier: str) -> models_pb2.OfferGroup:
        request = grpc_pb2.GetOfferGroupRequest(id=identifier)

        try:
            response = await self._offers.GetOfferGroup(request, timeout=self._timeout)
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Offer group with ID '{id}' not found.".format(id=identifier),
                ) from exc

            raise UnknownError() from exc

        return response.group

    async def find_groups_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferGroupsResponse:
        request = grpc_pb2.ListOfferGroupsRequest(
            page_token=cursor or "",
            offer_group_ids=grpc_pb2.ListOfIds(ids=list(identifiers)),
        )

        if limit is not None:
            request.page_size = limit

        try:
            return await errors.handle_grpc_errors(
                self._offers.ListOfferGroups(request, timeout=self._timeout),
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError() from exc

    async def get_group_details_by_id(self, identifier: str) -> models_pb2.OfferSegment:
        request = grpc_pb2.GetOfferGroupDetailsRequest(id=identifier)

        try:
            response = await errors.handle_grpc_errors(
                self._offers.GetOfferGroupDetails(request, timeout=self._timeout),
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Offer group details with ID '{id}' not found.".format(
                        id=identifier,
                    ),
                ) from exc

            raise UnknownError() from exc

        return response.details

    async def find_group_details_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferGroupDetailsResponse:
        request = grpc_pb2.ListOfferGroupDetailsRequest(
            page_token=cursor or "",
            offer_group_details_ids=grpc_pb2.ListOfIds(ids=list(identifiers)),
        )

        if limit is not None:
            request.page_size = limit

        try:
            return await errors.handle_grpc_errors(
                self._offers.ListOfferGroupDetails(request, timeout=self._timeout),
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError() from exc

    async def get_option_by_id(self, identifier: str) -> models_pb2.Offer:
        request = grpc_pb2.GetOfferOptionRequest(id=identifier)

        try:
            response = await self._offers.GetOfferOption(request, timeout=self._timeout)
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Option with ID '{id}' not found.".format(id=identifier),
                ) from exc

            raise UnknownError() from exc

        return response.option

    async def find_options_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferOptionsResponse:
        request = grpc_pb2.ListOfferOptionsRequest(
            page_token=cursor or "",
            offer_option_ids=grpc_pb2.ListOfIds(ids=list(identifiers)),
        )

        if limit is not None:
            request.page_size = limit

        try:
            return await errors.handle_grpc_errors(
                self._offers.ListOfferOptions(request, timeout=self._timeout),
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError() from exc

    async def get_option_details_by_id(
        self,
        identifier: str,
    ) -> models_pb2.OfferSegmentDetails:
        request = grpc_pb2.GetOfferOptionDetailsRequest(id=identifier)

        try:
            response = await self._offers.GetOfferOptionDetails(
                request,
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(
                    "Option details with ID '{id}' not found.".format(id=identifier),
                ) from exc

            raise UnknownError() from exc

        return response.details

    async def find_option_details_by_ids(
        self,
        identifiers: Sequence[str],
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> grpc_pb2.ListOfferOptionDetailsResponse:
        request = grpc_pb2.ListOfferOptionDetailsRequest(
            page_token=cursor or "",
            offer_option_details_ids=grpc_pb2.ListOfIds(ids=list(identifiers)),
        )

        if limit is not None:
            request.page_size = limit

        try:
            return await errors.handle_grpc_errors(
                self._offers.ListOfferOptionDetails(request, timeout=self._timeout),
            )
        except grpc.aio.AioRpcError as exc:
            raise UnknownError() from exc
