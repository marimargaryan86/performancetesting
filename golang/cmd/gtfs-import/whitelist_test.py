import json
from pathlib import Path
from typing import Literal

from pydantic import parse_obj_as

DATASETS_PATH = Path(__file__).with_name("datasets.json")
WHITELIST_PATH = Path(__file__).with_name("routes-whitelist.json")
TYPES = Literal["air", "rail", "ferry", "bus"]


class TestWhitelist(object):
    async def test_routes_whitelist(self) -> None:
        with WHITELIST_PATH.open() as fl:
            raw_data = json.load(fl)

        validated_whitelists = parse_obj_as(dict[str, list[TYPES]], raw_data)
        assert all(va for va in validated_whitelists.values())

        with DATASETS_PATH.open() as fl:  # noqa: WPS440
            datasets = json.load(fl)

        for dataset in datasets:
            assert (
                dataset["name"] in validated_whitelists
            ), "Dataset missing in routes-whitelist"

        assert "ssim" in validated_whitelists
        assert "directferries" in validated_whitelists
