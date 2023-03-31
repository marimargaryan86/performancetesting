import json
from pathlib import Path

from pydantic import parse_obj_as

from snowfall.project.junction.go.service.data_pipeline.download import Dataset

DATASETS_PATH = Path(__file__).with_name("datasets.json")


class TestDatasets(object):
    async def test_datasets_valid(self) -> None:
        with DATASETS_PATH.open() as fl:
            datasets = json.load(fl)

        validated_datasets = parse_obj_as(list[Dataset], datasets)

        assert any(ds["active"] for ds in validated_datasets)
