import lagom
from starlette import endpoints, exceptions, requests, responses, status

from snowfall.project.junction.plus.adapter import (
    monitoring_rules as monitoring_rules_adapter,
)


class Alerts(endpoints.HTTPEndpoint):
    async def post(
        self,
        request: requests.Request,
        monitoring_rules_client: monitoring_rules_adapter.Client = lagom.injectable,
    ) -> responses.Response:
        alert_body = await request.json()
        for name_value in alert_body["alert"]["rule"]["nameValues"]["nameValue"]:
            if name_value["name"] == "resource_id":
                monitoring_rule_id = name_value["value"]
                break
        else:
            raise exceptions.HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        await monitoring_rules_client.get(monitoring_rule_id)

        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)
