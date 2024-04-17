"""Download all gtfs files.

Fetches the datasets listed in datasets.json.

Basic auth credentials can be passed with environment variables.
PIPELINE_[name]_USERNAME and PIPELINE_[name]_PASSWORD, where name is defined in
datasets.json. For example: PIPELINE_GTFS_DE_USERNAME=some_user
"""

import asyncio
import json
import os
from collections.abc import Awaitable, Callable, Iterable
from pathlib import Path
from types import MappingProxyType
from typing import Any, TypeAlias

import httpx

from snowfall.project.junction.go.service.data_pipeline.distribusion_plugin import (
    distribusion_plugin,
)
from snowfall.project.junction.go.service.data_pipeline.obb_plugin import obb_plugin
from snowfall.project.junction.go.service.data_pipeline.sbb_plugin import sbb_plugin
from snowfall.project.junction.go.service.data_pipeline.types import Dataset
from snowfall.stdlib.service import application

_PluginResult = Iterable[dict[str, Any]]
_Plugin = Callable[[httpx.AsyncClient, Dataset], Awaitable[_PluginResult]]
PLUGINS: MappingProxyType[str, _Plugin] = MappingProxyType(
    {"OBB": obb_plugin, "SBB": sbb_plugin, "distribusion": distribusion_plugin},
)


class DownloadSettings(application.Settings):
    path: Path


_DownloadApp: TypeAlias = application.Application[DownloadSettings]


def _auth(name: str) -> tuple[str, str] | None:
    env_name = name.upper().replace(".", "_")
    username = os.environ.get("PIPELINE_{e}_USERNAME".format(e=env_name))
    password = os.environ.get("PIPELINE_{e}_PASSWORD".format(e=env_name), "")
    return (username, password) if username else None


async def _get_args(
    sess: httpx.AsyncClient,
    dataset: Dataset,
    auth: tuple[str, str] | None,
) -> tuple[dict[str, Any], ...]:
    base_args: dict[str, Any] = {"url": dataset["url"], "auth": auth}
    plugin = PLUGINS.get(dataset["name"])
    if plugin:
        request_args = tuple(base_args | di for di in await plugin(sess, dataset))
    else:
        request_args = (base_args,)

    if not request_args:
        raise RuntimeError("No files to fetch for {n}".format(n=dataset["name"]))

    return request_args


async def download_url(  # noqa: WPS231
    settings: DownloadSettings,
    sess: httpx.AsyncClient,
    dataset: Dataset,
) -> None:
    """Download the data for the given dataset definition."""
    name = dataset["name"]
    auth = _auth(name)
    request_args = await _get_args(sess, dataset, auth)

    for it, args in enumerate(request_args):
        suffix = "-{i}".format(i=it) if it > 0 else ""
        data_file_path = settings.path / "{n}{s}.zip".format(n=name, s=suffix)
        async with sess.stream("GET", **args) as resp:
            if not resp.is_success:
                msg = "Error fetching {n}: {s} (auth={a}):\n{b!r}".format(
                    n=name,
                    s=resp.status_code,
                    a=auth,
                    b=await resp.aread(),
                )
                raise RuntimeError(msg)
            if "zip" not in resp.headers["Content-Type"].lower():
                msg = "({n}) Incorrect content_type: {t}\nResponse: {c!r}"
                resp_content = await resp.aread()
                msg = msg.format(n=name, t=resp.headers["Content-Type"], c=resp_content)
                raise RuntimeError(msg)

            with data_file_path.open("wb") as zip_file:
                async for chunk in resp.aiter_bytes(2**20):  # noqa: WPS432
                    zip_file.write(chunk)

    print(  # noqa: T201,WPS421
        "DONE: {n} (country: {c})".format(n=name, c=dataset["country"]),
    )


async def run_download(app: _DownloadApp) -> None:
    """Entry point to start downloads."""
    app.settings.path.mkdir(parents=True, exist_ok=True)

    with Path(__file__).with_name("datasets.json").open() as fl:
        datasets: list[Dataset] = json.load(fl)

    headers = {"User-Agent": "Snowfall Travel"}
    async with httpx.AsyncClient(
        timeout=600,  # noqa: WPS432
        headers=headers,
        follow_redirects=True,
    ) as sess:  # noqa: WPS432
        ts = (download_url(app.settings, sess, ds) for ds in datasets if ds["active"])
        await asyncio.gather(*ts)


if __name__ == "__main__":
    entrypoint = application.Entrypoint(name="junction-go-data-pipeline")
    entrypoint.enter_with_commands(
        application.Command(
            name="download",
            callback=run_download,
            settings_class=DownloadSettings,
        ),
    )
