import copy
import datetime
from collections.abc import Mapping, Sequence
from typing import Any

import httpx
import qrcode
import xmltodict
from PIL import Image, ImageDraw, ImageFont

from snowfall.project.junction.plus.service.poc_api import airlines
from snowfall.stdlib.persistence import filesystem


class TravelFusionClient(object):
    def __init__(
        self,
        api_url: str,
        client_key: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client_key = client_key
        self._client = client or httpx.AsyncClient()
        self._client.base_url = httpx.URL(api_url)

    async def checkin_availability(self, airline_code: str, route_code: str) -> int:
        json_data = copy.deepcopy(tf_availability)
        command = json_data["CommandList"]["CheckinAvailabilityPlane"]
        command["XmlLoginId"] = self._client_key
        command["LoginId"] = self._client_key
        command["Airline"]["TFCode"] = airline_code
        command["Criteria"]["AirportcodeRoute"] = route_code
        xml_data = json2xml(json_data)
        response = await self._make_request(
            payload=xml_data,
        )
        commands = xmltodict.parse(response.text)["CommandList"]
        if "CommandExecutionFailure" in commands:
            return 0
        return int(
            commands["CheckinAvailabilityPlane"]["AdvanceAvailabilityList"][
                "AdvanceAvailability"
            ]["From"],
        )

    async def _make_request(
        self,
        payload: str,
    ) -> httpx.Response:
        headers = {
            "Content-Type": "text/xml",
            "Accept": "text/xml",
        }
        return await self._client.request(
            method="POST",
            url="",
            headers=headers,
            data=payload,  # type: ignore[arg-type]
        )


def json2xml(
    json_obj: Mapping[Any, Any] | Sequence[Any],
    line_padding: str = "",
) -> str:
    if isinstance(json_obj, list):
        return "\n".join([json2xml(sub_elem, line_padding) for sub_elem in json_obj])

    if isinstance(json_obj, dict):
        result_list: list[str] = []

        for tag_name, sub_obj in json_obj.items():
            result_list.extend(
                (
                    "{0}<{1}>".format(line_padding, tag_name),
                    json2xml(sub_obj, line_padding),
                    "{0}</{1}>".format(line_padding, tag_name),
                ),
            )

        return "".join(result_list)

    return "{0}{1}".format(line_padding, json_obj)


tf_availability: dict[str, Any] = {
    "CommandList": {
        "CheckinAvailabilityPlane": {
            "XmlLoginId": "XmlLoginId",
            "LoginId": "LoginId",
            "Airline": {
                "TFCode": "TFCode",
            },
            "Criteria": {
                "AirportcodeRoute": "AirportcodeRoute",
                "TravellerList": {
                    "Traveller": {
                        "Age": 30,
                        "IdCountryOfIssue": "GR",
                    },
                },
            },
        },
    },
}


def create_boarding_pass(
    order: Mapping[str, Any],
) -> Image.Image:
    width, height = 500, 600
    img = Image.new("RGB", (width, height), color="#47ab93")
    draw = ImageDraw.Draw(img)
    detail = order["bookings"][0]["details"][0]
    leg = detail["legs"][0]
    boarding_window = 30
    departure = datetime.datetime.fromisoformat(
        leg["departureAt"],
    ) - datetime.timedelta(minutes=boarding_window)
    passenger = order["passengers"][0]

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data("BoardingPass")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#353c45", back_color="#ffffff")
    qr_x = 120
    qr_y = 340
    img.paste(qr_img, (qr_x, qr_y))
    font_pkg = filesystem.resource_path(
        package="snowfall.project.junction.plus.service.poc_api.travel_fusion",
        resource="arial.ttf",
    )
    font_size = 20
    font = ImageFont.truetype(str(font_pkg.absolute()), font_size)
    text_color = "#ffffff"
    text_color2 = "#353c45"
    draw.text(
        (width / 2, 50),
        airlines.airlines_mapping.get(detail["operator"], ""),
        font=font,
        fill=text_color,
        anchor="ms",
    )

    draw.text((50, 90), "From", font=font, fill=text_color2)
    draw.text(
        (110, 90),
        leg["origin"]["name"],
        font=font,
        fill=text_color,
    )
    draw.text((50, 120), "To", font=font, fill=text_color2)
    draw.text(
        (110, 120),
        leg["destination"]["name"],
        font=font,
        fill=text_color,
    )

    draw.text((50, 170), "Flight", font=font, fill=text_color2)
    draw.text(
        (150, 170),
        detail["vendor"] + detail["routeIdentifiers"]["vendor"],
        font=font,
        fill=text_color,
    )
    draw.text((300, 170), "Class", font=font, fill=text_color2)
    draw.text((400, 170), detail["cabinClassName"], font=font, fill=text_color)
    draw.text((50, 200), "Date", font=font, fill=text_color2)
    draw.text(
        (150, 200),
        departure.strftime("%m/%d/%Y"),
        font=font,
        fill=text_color,
    )
    draw.text((300, 200), "Boarding", font=font, fill=text_color2)
    draw.text(
        (400, 200),
        departure.strftime("%H:%M"),
        font=font,
        fill=text_color,
    )

    draw.text((50, 260), "Passenger", font=font, fill=text_color2)
    draw.text(
        (50, 290),
        "{0} {1}".format(passenger["firstName"], passenger["lastName"]),
        font=font,
        fill=text_color,
    )
    draw.text((300, 260), "Seat", font=font, fill=text_color2)
    draw.text((300, 290), "12A", font=font, fill=text_color)

    return img
