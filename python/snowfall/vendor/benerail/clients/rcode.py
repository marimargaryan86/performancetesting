from snowfall.stdlib.transport.http import client
from snowfall.vendor.benerail.clients import base
from snowfall.vendor.benerail.models.enumeration import response as rcodes_response

_BASE_RCODE_PATH = "/rcode/rcode"
_BASE_RCODE_TYPE_PATH = "/rcode/rcode-types"
_BASE_RCODE_AUTHORIZATION_PATH = "/rcode/authorization-groups"
_BASE_PLACE_PATH = "/rcode/places"


class RcodeClient(base.BenerailBaseClient):
    async def get_all_url_token_values(
        self,
        url_token: str,
    ) -> rcodes_response.RcodesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/{url_token}".format(
                    rcode_prefix=_BASE_RCODE_PATH,
                    url_token=url_token,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.RcodesResponse(**response.json())

    async def get_urn_value(
        self,
        urn: str,
    ) -> rcodes_response.RcodesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/{urn}".format(
                    rcode_prefix=_BASE_RCODE_PATH,
                    urn=urn,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.RcodesResponse(**response.json())

    async def get_database_info(
        self,
        type_id: str,
        code_id: str,
    ) -> rcodes_response.RcodesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/id/{type_id}/{code_id}".format(
                    rcode_prefix=_BASE_RCODE_PATH,
                    type_id=type_id,
                    code_id=code_id,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.RcodesResponse(**response.json())

    async def get_rcode_attributes(
        self,
        type_id: str,
        code_id: str,
    ) -> rcodes_response.AttributesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/id/{type_id}/{code_id}/attributes".format(
                    rcode_prefix=_BASE_RCODE_PATH,
                    type_id=type_id,
                    code_id=code_id,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.AttributesResponse(**response.json())

    async def get_rcode_with_namespace(
        self,
        namespace: str,
        rcode_type: str,
        code: str,
    ) -> rcodes_response.AttributesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/{namespace}/{rcode_type}/{code}".format(
                    rcode_prefix=_BASE_RCODE_PATH,
                    namespace=namespace,
                    rcode_type=rcode_type,
                    code=code,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.AttributesResponse(**response.json())

    async def get_authorization_groups(
        self,
    ) -> rcodes_response.AuthorizationGroupsResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path=_BASE_RCODE_AUTHORIZATION_PATH,
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.AuthorizationGroupsResponse(**response.json())

    async def get_authorization_group(
        self,
        group_id: str,
    ) -> rcodes_response.AuthorizationGroupsResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/{group_id}".format(
                    rcode_prefix=_BASE_RCODE_AUTHORIZATION_PATH,
                    group_id=group_id,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.AuthorizationGroupsResponse(**response.json())


class RcodeTypeClient(base.BenerailBaseClient):
    async def get_namespace_values_for_rcode_type(
        self,
        rcode_type: str,
    ) -> rcodes_response.RcodesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/{rcode_type}".format(
                    rcode_prefix=_BASE_RCODE_TYPE_PATH,
                    rcode_type=rcode_type,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.RcodesResponse(**response.json())

    async def get_attribute_types_for_rcode_type(
        self,
        rcode_type: str,
    ) -> rcodes_response.AttributeTypesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/{rcode_type}/attribute-types".format(
                    rcode_prefix=_BASE_RCODE_TYPE_PATH,
                    rcode_type=rcode_type,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.AttributeTypesResponse(**response.json())

    async def get_attribute_type_for_rcode_type(
        self,
        rcode_type: str,
        attribute_type: str,
    ) -> rcodes_response.AttributeTypesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/{rcode_type}/attribute-types/{attribute}".format(
                    rcode_prefix=_BASE_RCODE_TYPE_PATH,
                    rcode_type=rcode_type,
                    attribute=attribute_type,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.AttributeTypesResponse(**response.json())

    async def get_authorization_settings(
        self,
        rcode_type: str,
    ) -> rcodes_response.AuthorizationsResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/{rcode_type}/authorizations".format(
                    rcode_prefix=_BASE_RCODE_TYPE_PATH,
                    rcode_type=rcode_type,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.AuthorizationsResponse(**response.json())

    async def get_rcode_types(
        self,
    ) -> rcodes_response.TypesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path=_BASE_RCODE_TYPE_PATH,
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.TypesResponse(**response.json())


class Place(base.BenerailBaseClient):
    async def get_places(
        self,
    ) -> rcodes_response.PlacesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path=_BASE_PLACE_PATH,
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.PlacesResponse(**response.json())

    async def get_place(
        self,
        urn: str,
    ) -> rcodes_response.PlacesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/{urn}".format(
                    rcode_prefix=_BASE_PLACE_PATH,
                    urn=urn,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.PlacesResponse(**response.json())

    async def get_place_with_value_for_namespace(
        self,
        namespace: str,
        place_type: str,
        value_str: str,
    ) -> rcodes_response.PlacesResponse:
        response = await self._make_request(
            client.RequestOptions(
                method="GET",
                path="{rcode_prefix}/{namespace}/{place_type}/{value_str}".format(
                    rcode_prefix=_BASE_PLACE_PATH,
                    namespace=namespace,
                    place_type=place_type,
                    value_str=value_str,
                ),
                headers=self._auth_headers,
            ),
        )

        return rcodes_response.PlacesResponse(**response.json())
