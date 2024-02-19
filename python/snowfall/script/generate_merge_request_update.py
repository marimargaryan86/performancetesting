import collections
import datetime
import sys
from collections.abc import Iterator
from typing import cast

import gitlab
import numpy as np
from gitlab.v4 import objects


def time_ago_emoji(updated_at: datetime.datetime) -> str:
    now = datetime.datetime.now(tz=datetime.UTC)
    diff = datetime.timedelta(
        days=int(
            np.busday_count(updated_at.date().isoformat(), now.date().isoformat()),
        ),
    )

    if diff < datetime.timedelta(days=1):
        return "😍"

    if diff < datetime.timedelta(days=3):
        return "🙂"

    if diff < datetime.timedelta(days=6):
        return "😴"

    return "🥶"


def time_ago_string(updated_at: datetime.datetime) -> str:
    now = datetime.datetime.now(tz=datetime.UTC)
    diff = now - updated_at

    if diff.days > 0:
        return "{0} days".format(diff.days)

    return "{0} hours".format(round(diff.total_seconds() / 60 / 60))


if len(sys.argv) < 3:
    raise SystemExit

gl = gitlab.Gitlab(url="https://git.snowfall.se", private_token=sys.argv[1])
project = gl.projects.get(sys.argv[2])
merge_requests = cast(
    Iterator[objects.ProjectMergeRequest],
    project.mergerequests.list(
        iterator=True,
        state="opened",
        order_by="updated_at",
        sort="desc",
    ),
)
statuses = collections.defaultdict(list)

for merge_request in merge_requests:
    if merge_request.draft:
        continue

    try:
        status = next(
            label.removeprefix("status::").title()
            for label in merge_request.labels
            if label.startswith("status::")
        )
    except StopIteration:
        continue

    statuses[status].append((
        merge_request.title,
        merge_request.web_url,
        ", ".join(assignee["name"] for assignee in merge_request.assignees)
        if status == "Review Needed"
        else merge_request.author["name"],
        datetime.datetime.fromisoformat(merge_request.updated_at),
    ))


output_message = ""


for status_name, items in (dict(sorted(statuses.items()))).items():
    output_message += "*{0}*\n".format(status_name)
    output_message += "\n".join(
        "{4} _<{1}|{0}> assigned to {2} (no activity for {3})_".format(
            item[0],
            item[1],
            item[2],
            time_ago_string(item[3]),
            time_ago_emoji(item[3]),
        )
        for item in items
    )

    output_message = "{0}\n\n".format(output_message)


print(output_message)  # noqa: T201,WPS421
