# PSS API V2

This section of the `Junction` Monorepo is related to the migration of PSS API
from PHP 5.6 into Python 3.11+ and everything that goes with it.

To develop on PSS API V2, you will need all the pre-requisites for the `Junction`
Monorepo, you will also need to have installed:

* `mysql` (See [Homebrew installation](https://formulae.brew.sh/formula/mysql))

## Local development setup

As the current PSS API lives in https://git.snowfall.se/junctionbase/tardis, you
will probably want this locally for reference to V1.

You then need to download: https://drive.google.com/file/d/1mW6ism2Qw6kGcPYmCPV_yptEEAOGaYpe/view?usp=share_link
extract the contents and place it somewhere accessible.

You can then run (from the root of the `Junction` Monorepo):

```shell
docker-compose -f python/snowfall/project/pss/docker-compose.yml up -d
```

This will stand up the MySQL database that we will import PSS data into.

You will need to copy the dump into the container:

```shell
docker cp <path/to/dump.sql> <container-name>:/
```

Finally, you will need to exec onto the database container and import the dump:

```
docker exec -it <container-name> bash

# You are now in the container:

mysql --password=password tardis < /dump.sql
```

This will take a few minutes, but once done you will have data within your database

## Running PSS API 2 locally

To run PSS API 2 locally, use (from the root of the `Junction` Monorepo):

```
bash ./bash/run.sh python/snowfall/project/pss/service/api/main.py http
```

You can then make requests to the URL output in the logs:

```
17:07:40.90 [INFO] Completed: Building 31 requirements for python.snowfall.project.pss.service.pss_api_v2/main.pex from the vendor/lock/constraints.txt resolve: SQLAlchemy==2.0.0, aiofiles==22.1.0, asgiref==3.6.0, click==8.1.3, email-val... (601 characters truncated)
{"name":"api","version":"dev","environment":"local","event":"Application bootstrapped.","source":"application","logger":"snowfall.stdlib.service","level":"info","timestamp":"2023-01-30T17:07:42.527359Z"}
{"event":"Started server process [52922]","source":"application","logger":"uvicorn.error","level":"info","timestamp":"2023-01-30T17:07:42.534786Z"}
{"event":"Waiting for application startup.","source":"application","logger":"uvicorn.error","level":"info","timestamp":"2023-01-30T17:07:42.534861Z"}
{"event":"Application startup complete.","source":"application","logger":"uvicorn.error","level":"info","timestamp":"2023-01-30T17:07:42.534997Z"}
{"event":"Uvicorn running on http://127.0.0.1:8005 (Press CTRL+C to quit)","source":"application","logger":"uvicorn.error","level":"info","timestamp":"2023-01-30T17:07:42.535219Z"}
```

## Functionality not to be implemented

Because PSS is an amalgamation of lots of projects, Ragusa doesn't need all of
the current functionality which could potentially lead to less re-write work.

High level over-arching things include:

* Not worrying about `loyalty`
* Not worrying about `mailchimp` usage
* Not worrying about `psp`

### /transactions

`Addons` are mentioned a lot in `POST` `/transactions`, for now, they are to be
ignored as not used by Ragusa from our understanding.

We are not using `affiliate_id`s.
