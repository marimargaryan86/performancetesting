---
internal: true
---

# Time Slice Planner

[TOC]

Author: Simon Hewitt

Date: May 2023.     Version 0.1

File in repo : `golang/cmd/gtfs-timeslice-import/timeslice-planner.md`

Branch: `653-time-slice`



This document describes two related developments, the prototype **timeslice planner** with its associated changes to data preparation, and the **end to end planner tests ** that verify the planner is operating as expected. The document also comprises both a user manual and a technical description of both elements.

---

## Part 1 - Timeslice Planner

The `planner` component is a core element of **Go** which, given an origin and a destination and a departure time, returns suitable journey routes. One of the technical challenges is the huge amount of data that the Planner requires to describe routes, both as flat files and then as in-memory copies of these files.

For some time we have been proposing a method to run multiple instances of the planner, each covering a different time period, with a "router" that directs each query to the appropriate planner instance - the `timeslice-planner`. A prototype is now ready, described here. First we will describe the changes to the data preparation, then the timeslice-planner itself.



### time-slice.json

The core idea is that we will run a number of planner instances, each covering a specific time period. These time periods must be defined as contiguous, and an overlap is added to the end of each instance to allow for long running journeys. The time slices are defined, for all processes that need awareness of the time-slices, in a JSON file, nominally `golang/cmd/gtfs-timeslice-import/time-slice.json`. (But note, all programs that use the time-slice file received the file path as a run-time parameter.)

Example time-slice.json with 6 periods.

```
{
  "rubric": {
    "name": "Test TimeSlice",
    "issue_date": "27/3/2023",
    "plan_start_date": "1/4/2023T00:00:01",
    "plan_end_date": "",
    "version": "1.0",
    "comment": "This is a test & development time slice definition",
    "after_overlap_hours": 72
  },
  "periods": [
    {
      "name": "p1",
      "end_date": "2023-01-14",
      "port": 50061
    },
    {
      "name": "p2",
      "end_date": "2023-2-14",
      "port": 50062
    },
    {
      "name": "p3",
      "end_date": "2023-3-14",
      "port": 50063
    },
    {
      "name": "p4",
      "end_date": "2023-06-01",
      "port": 50064
    },
    {
      "name": "p5",
      "end_date": "2023-12-01",
      "port": 50065
    },
    {
      "name": "p6",
      "end_date": "",
      "port": 50066
    }
  ]
}

```



The file has two top-level components:



**rubric** This section contains mostly description text, to help manage file versions and purposes. The one essential data element is  `after_overlap_hours`, the overall period between time slices, which must be equal or greater than  the planner maximum journey length - 72 hours in the example above.

The **periods** section describes the periods themselves. We recommend two or more periods (one may work, but has not been tested). Each period has:

| Field    | Purpose                                                      | Example             |
| -------- | ------------------------------------------------------------ | ------------------- |
| name     | This is used to refer to the periods, and is used as the final leaf of the data path (so must be a valid Unix path element) | `p1`, `late_summer` |
| end_date | The end of the. time-slice period, `yyyy-mm-dd`. **NOTE MUST** be blank "" for the last timeslice. The first period is always from the beginning of the route data to the period 1 end-date. | 2023-01-01          |
| port     | The port that will be used by the planner instance(s) for this timeslice | 50064               |

**Notes:**

Name - KISS [^1]. `p1` is good.

Port - obviously must not be used for anything else, in particular don't use 50053, this is used by the timeslice-planner gateway.

**File Location** The file path is passed to all utilities that use it as a command line parameter (such as `--time-slice-json`), the only requirement is that the file is readable (no write needed) and filename suffix is `.json`.

**Default file** If no file is specified, then default file `golang/cmd/gtfs-timeslice-import/time-slice-default.json` is used

- [ ] scrap this? Crash if not specified or found?

**File Error** If the file is not readable, the programs generally panic (or log.fatal), they cannot proceed without a valid definition file.

Note that by specifying only end-date, we avoid any issues with contiguous periods. P1 runs from the beginning of time to the  P1 end date, each subsequent period runs from the preceding period to it's end date, except the last period which runs to 'the end of time' . Obviously only routes actually in the dataset will be found!

[^1]: KISS:- Keep It Simple mate

### gtfs-timeslice-import

`gtfs-timeslice-import` replaces `gtfs-import` to create per-timeslice datasets. The core data processing is the same as `gtfs-import`, but the decision to create a new program was made to allow simple and clear switch from 'classic' to time-slice working.

`gtfs-timeslice-import`  requires one new command line parameter, the time slice definition file.

```
Requires command line parameters for:
  1) --input-dir,  Path to the GTFS ZIP files
  2) --output-dir, Directory for the output files (the intermediate data files)
  3) --cutoff-days, (Optional) number of days into the future to include data
    (helpful to create smaller test datasets).
  4) --run-date (Optional), start-date for including routes (default is time.Now())
  5) --time-slice-json The time-slice JSON definition file
```

It picks up `gtfs` files from the `--input-dir` as currently. Using `--output-dir` , we create a subdirectory for each timeslice, using the time-slice name, thus (if --output-dir is `/feeds/transitional_data`):

```
# ls /feeds/transitional_data/*
transitional_data/_summary.dat  transitional_data/locations.bson  transitional_data/schedules.bson

transitional_data/p1:
_timeslice  locations.bin  schedules.bin

transitional_data/p2:
_timeslice  locations.bin  schedules.bin

transitional_data/p3:
_timeslice  locations.bin  schedules.bin

transitional_data/p4:
_timeslice  locations.bin  schedules.bin

transitional_data/p5:
_timeslice  locations.bin  schedules.bin

transitional_data/p6:
_timeslice
```

So there is a complete and consistent set of route data in each period sub-directory. Note that there are still just two `.bson` files, `transitional_data/locations.bson` and `  transitional_data/schedules.bson`. These are used to load the MongoDB database, and still contain the entire dataset.

- [ ] Add time-slice to Mango data?



File `_summary.dat` just records the rows for each slice:

```
# cat transitional_data/_summary.dat
*** Period Time Slice Summary ***
Period:         p1  from: nil         to: 2023-01-16  Schedules:      37498
Period:         p2  from: 2023-01-14  to: 2023-02-16  Schedules:      199858
Period:         p3  from: 2023-02-14  to: 2023-03-16  Schedules:      194346
Period:         p4  from: 2023-03-14  to: 2023-06-03  Schedules:      583428
Period:         p5  from: 2023-06-01  to: 2023-12-03  Schedules:      1359092
Period:         p6  from: 2023-12-01  to: nil         Schedules:      518701
Total periods:  6                                     Total Schedules 2892923
```

And the `_timeslice` file in each timeslice directory has a detailed summary for the period:

```
cat feeds/transitional_data/p1/_timeslice
*** Time Slice Data Directory ***
Name:                              p1
Start Date:                        nil
Computed End Date (with overlap):  2023-01-16
Base End Date (no overlap):        2023-01-14
Time Slice definition name:        Test TimeSlice
Time Slice definition version :    1.0
Created date :                     2023-05-17T09:13:20Z

* Time Slice Summary *
Total schedules:    37498
Earliest schedule:  2023-01-02T00:01:00Z
Latest schedule:    2023-01-13T23:59:00Z
```

- [ ] ToDo: More useful details in summary files eg timeslice file, maybe runtime?

**NOTES**

The data in each dataset is actually from the period start-time to the period end-time PLUS the `after_overlap_hours`, so that journeys starting near or at the end-time can still be calculated, up to the maximum journey time.

### timeslice-schedules-export

Program `timeslice-schedules-export.go` (`golang/cmd/timeslice-schedules-export/timeslice-schedules-export.go`) is a small program that reads the `time-slice.json` file, and starts an (unchanged)  `schedules-export.go` instance for each period. It assumes that `gtfs-timeslice-import` has run before to create the intermediate `locations.bin` and  ` schedules.bin` files. Thus the output is a number of datafile sets, exactly the same as now, repeated for each period:

```
# ls /feeds/output_data/*
/feeds/output_data/_summary.dat

/feeds/output_data/p1:
_sizes  route_stops.bin  routes.bin  schedule_stops.bin  schedules.bin  stops.bin  transfers.bin

/feeds/output_data/p2:
_sizes  route_stops.bin  routes.bin  schedule_stops.bin  schedules.bin  stops.bin  transfers.bin

/feeds/output_data/p3:
_sizes  route_stops.bin  routes.bin  schedule_stops.bin  schedules.bin  stops.bin  transfers.bin

/feeds/output_data/p4:
_sizes  route_stops.bin  routes.bin  schedule_stops.bin  schedules.bin  stops.bin  transfers.bin

/feeds/output_data/p5:
_sizes  route_stops.bin  routes.bin  schedule_stops.bin  schedules.bin  stops.bin  transfers.bin

/feeds/output_data/p6:
_sizes  route_stops.bin  routes.bin  schedule_stops.bin  schedules.bin  stops.bin  transfers.bin
```

The `_summary.dat` lists the created time:

```
# cat /feeds/output_data/_summary.dat
*** Period Time Slice Output Data Summary ***
Created at: 2023-05-17T09:15:18Z
schedules-export executable is: cmd/schedules-export/schedules-export
```

And the per period `_sizes` file contains the row counts by data type :

```
# cat /feeds/output_data/p2/_sizes
scheduleStops 400414
schedules 199858
routeStops 8239
routes 4094
stops 737
```

- [ ] ToDo: More useful details in summary files eg timeslice file, maybe runtime? -

The program parameters are:

|Option|Default|Typical value|Purpose|
|---|---|---|---|
|--input-dir| |/feeds/transitional_data|Input directory containing the intermediate BIN files|
|--output-dir| |/feeds/output_data|Output directory where the output BIN files will be placed|
|--sched-prog| |cmd/schedules-export/schedules-export|Full path for the schedules-export executable (compiled Go) file|
|--time-slice-json|time-slice.json|/feeds/test_data/time-slice.json|Time slice JSON definition file|
|--verbose| false|false|--verbose to get lots of useful output|

**NOTES**

1. --sched-prog identifies the existing export program, which is unchanged (but in turn receives period-specific input and output directories)

As the existing `schedules-export` programs run independently with different input and output datasets, they are run concurrently, using Go routines. This provides a useful reduction in run time.

### timeslice-planner.go

(`golang/cmd/timeslice-planner/timeslice-planner.go`)

A feature of the design is that the existing planner is run entirely unchanged, from the program "internal" perspective. From the "external" perspective, one (or more) instance(s) are started per time period, with the appropriate path to the `.bin` data files.

![timeslice-planner](/Users/simonh/repos/595-rebase-55/docs/readme-images/timeslice-planner.png)

`timeslice-planner` operates as a router. It serves port 50053, the existing Planner port, it determines which time slice period serves the request and forwards the request to the correct planner instance. The response is passed back to the caller unchanged.  `timeslice-planner` uses the same `grpcServer` framework as `planner`.

Program Options:

|Option|Default|Typical value|Purpose|
|---|---|---|---|
|--server-port| 50053|50053|timeslice-planner will server the Planner gRPC on this port|
|--planner-uri|localhost|| Planner gRPC Server address |
|--time-slice-json| /feeds/test_data/time-slice.json|time-slice.json| Time slice JSON definition file|
|--verbose| false |false|--verbose to get lots of useful output|
|--bin-dir| | /feeds/output_data |Directory where time-slice planner BIN file directories are located (eg .../p1, .../p2 etc)|
|--start-planners| false|false| if True, starts one planner for each time slice|
|--prometheus-port| 0||Prometheus port, omit to skip Prometheus server|

**Notes**

`--start-planners` if `true` then one `planner` instance is started for each period, as a Go routine within the main `timeslice-planner` instance. This is intended for testing and development only, and is not production capable, as it does not:

* Restart on failure
* Monitor logs
* Cannot run multiple instances

None the less it has proved very useful for testing and development purposes.

`--verbose` is definitely quite noisy.

Note that if `--server-port` is 50053, then all upstream users of the Planner service can continue unaffected, and will not be aware of the change to timeslice operation.



### Changes to the data pipeline and deployment

The changes to the data pipeline are fairly minimal, replacing `gifs-import` with `gtfs-timeslice-import` and `schedules-export` with `timeslice-schedules-export`, and the associated directory setups etc. The testing script `bash/tests/schedule_tests/run_e2e_tests.sh` provides examples of how each program is run.

The Planner startup is a little more complex. Again look at `golang/cmd/timeslice-planner/timeslice-planner.go:func startPlanners` for a working example. The requirements is to:

1. Read the `time-slice.json` file
2. For each time-slice start one or more planner instances, specifying the data directory and the port for that timeslice
3. Start (one or more) `timeslice-planner` instances, serving 50053 - behind a load sharer if more than one instance.

**NOTE** that currentlythe ` timeslice-planner`program cannot load-share to multiple `planner` instances, and assumes a load-sharer device is handling any multiple-instance running. It would not be difficult to server a range of port numbers in a simple round-robin fashion.





## Part 2 - Planner E2E Tester



This section describes the test utility created to run the planner with a defined set of inputs and compare the results to a known good set.

The test sequence is:

1. Download a test definition file from an S3 bucket
2. This test definition file specifies other files to be downloaded from the same S3 bucket, these are the GTFS data, the 'known good' results file and the time-slice definition to be used.
3. The GTFS files are expanded from the tar ball and moved to /feeds/input_data
4. The data pipeline is executed, to create Planner `.bin` files.
5. The planner is started
6. Program `planner-test-client_test.go` is run, which uses the test-definition file to call the planner and compare the results with the expected results.
7. A test report is pushed to the S3 bucket, and a Slack message sent with 'SUCCESS" or 'FAIL' status.

The tests are run by the bash script `bash/tests/schedule_tests/run_e2e_tests.sh`, in a Docker container, described in detail below. The tests are intended to be run 'locally', on a developers or testers local PC.

### Test Files

#### Test Definition File

The Test Definition File must be saved on an S3 bucket that is accessible from the environment running the tests. The file is identified to the test script by environment variable (env var) `E2E_TEST_YML_FILE`. Such as `E2E_TEST_YML_FILE=s3://junction-schedules-export/Test/test_data/target_test.yml`. The YAML file uses YAML anchors and aliases, if you are unfamiliar with this construct, a good introduction can be found [here](https://www.educative.io/blog/advanced-yaml-syntax-cheatsheet#anchors).



Sample file:

```
---
test-details:
  name: These tests are used to prove the basic working of the time-slice planner.
  created-date: 2023-05-11T13:18:04Z
  created-by: Simon Hewitt
  gtfs-tar-file: s3://junction-schedules-export/Test/test_data/e2e_test_data.tar
  known-good-files: s3://junction-schedules-export/Test/test_data/target_test_run.tar.gz
  time-slice-json: s3://junction-schedules-export/Test/test_data/time-slice.json
  comment: >-
    Testing the tests.
    NOTE BA183 runs at different times on different dates.

test-data:
  - name: Test BA183-1 LHR JFK 2023-01-16 (first BA183 in the test data)
    skip: false
    input: &LHR_to_JFK
      from:
        Latitude: 51.470311
        Longitude: -0.458118
        name: LHR
      to:
        Latitude: 40.640556
        Longitude: -73.778519
        name: JFK
      afterTime: 2023-01-16T19:45:00.000+0
    known-good-file: "test-ba183-1"
    results: &LHR_to_JFK_results_19-45
      - testName: BA183 direct
        segments:
          - name: BA183
            agencyName: BA
            transportMode: air
            numberOfLegs: 1
            legs:
              - departure: Heathrow Airport
                departureTime: 19:45:00
                arrival: JFK
                arrivalTime: 03:45:00
      - testName: TK1984 & TK3
        segments:
          - name: TK1984
            agencyName: TK
            transportMode: air
            numberOfLegs: 1
            legs:
              - departure: Heathrow Airport
                departureTime: 22:35:00
                arrival: IST
                arrivalTime: 02:15:00
          - name: TK3
            agencyName: TK
            transportMode: air
            numberOfLegs: 1
            legs:
              - departure: Istanbul Airport
                departureTime: 05:50:00
                arrival: JFK
                arrivalTime: 16:50:00

```

The file has two top-level blocks, `test-details:` and `test-data:`.

`test-details:`  defines the test scope:

| Key                      | Purpose                                                      |
| ------------------------ | ------------------------------------------------------------ |
| name                     | An identifying name, recommended to be unique                |
| created-date, created-by | Who and When, for audit purposes                             |
| gtfs-tar-file            | A TAR archive of the GTFS files to be used in the tests. Keep it as small as possible for speed but with enough types of data for comprehensive tests. Must be an accessible S3 path. |
| known-good-files         | A zipped TAR archive of 'known-good' results, see below.     |
| time-slice-json          | The time-slice definition to be used                         |
| comment                  | Any useful notes. (In the example we use the `>-` YAML construct to recognise multi-line text data) |

`test-data` defines the tests themselves, as a YAML list of tests under the `-name` tag.

| Key                                   | Purpose                                                      |
| ------------------------------------- | ------------------------------------------------------------ |
| name                                  | Identify the test, must be unique within the file            |
| skip                                  | If `true`, this test is not executed. Default `false`        |
| input                                 | This group defines the raw data sent to the planner, see the example file above. The `name` tag is not part of the test data but is used to simplify identifying the tests, the `from` and `to` : `Latitude` and `Longitude`, and `afterTime` are mandatory. `afterTime` is ISO 8601 format. |
| known-good-file                       | This is the name of a file that will be used for the 'known-good' tests, see below. |
| results                               | This object defines the expected results. It comprises one or more objects identified by `testName` |
| testName                              | This comprises one or more `segments`                        |
| segments                              | Comprises one or more individual segments, identified by `name` |
| name                                  | (segment name) A segment expected to be in the Planner results. See the example above for the expected data. |
| legs                                  | Each result segment must cobntain onbe or more legs (matching the `numberOfLegs` value), which define an expected journey leg. This is the heart ion the tests, does the Planner return the  routes, segments and legs that we expect? |
| Legs:departure and legs:departureTime | The _full name_ and departure time for the leg, time is just `hh:mm:ss` |
| Legs:arrival and legs:arrivalTime     | The _code_ and time for the arrival.                         |

In practice it has been difficult to get these details exactly correct for a test run, and we have found it useful to run the tests with known 'bad' expected results and then examine the detailed test report to see what the planner returns to get exact details of node names and times. Obviously these results must be verified to ensure we are not just performing 'circular testing'.



#### gtfs-tar-file

This file is a TAR archive of GTFS files. GTFS files in turn are ZIP files containing a number of TXT files (see the GTFS definition at [google developer](https://developers.google.com/transit/gtfs)). The purpose is to ensure we can always run the tests against the exact same input data. The development has been done with file `s3://junction-schedules-export/Test/test_data/e2e_test_data.tar` which contains:

```
OBB.zip
ssim-a3.zip
ssim-ba.zip
ssim-lx.zip
ssim-tk.zip
```



#### time-slice-json

See section 1 for a full description of time-slice definition files. Again, it is saved on an S3 so tests are always run with the same time-slice definition. Development was done using file `s3://junction-schedules-export/Test/test_data/time-slice.json`.



#### known-good-files

See known-good testing, below.



### run_e2e_tests.sh

Tests are executed by `bash/tests/schedule_tests/run_e2e_tests.sh` Note, alias `run_e2e_tests`has been added to the Docker bash environment to run the test script, to reduce typing errors.

The script is large and somewhat 'organic', but the main structure is that it expects to run a Bash function in the form `run_xxxx`, with a command such as:

`bash/tests/schedule_tests/run_e2e_tests.sh run_tests`

Command

`bash/tests/schedule_tests/run_e2e_tests.sh list` will list all available commands, which are:

```
>> List of available functions
declare -f run_all_classic
declare -f run_all_timeslice
declare -f run_export
declare -f run_fetch_test_data
declare -f run_import
declare -f run_kill_planner
declare -f run_load_mongo
declare -f run_planner_tests
declare -f run_start_single_planner
declare -f run_start_timeslice_planner
declare -f run_startup
declare -f run_tests_timeslice
declare -f run_tests_classic
declare -f run_timeslice_export
declare -f run_validate
```

Although in general use should be restricted to the direct test commands described below, others are for development and debug use.

The main tests and other commands are:



#### Test Output

All test runs (`golang/cmd/planner-test-client/planner-test-client.go`) produce two output files, a `.CSV` summary and a `.HTML` detailed report as an HTML page. The filenames are `results_<utc-timestamp>.csv` and `.html`, and uploaded to an S3 bucket. The S3 path is currently hard coded in `run_e2e_tests.sh` as `S3/junction-schedules-export/Test/test_data/logs/`

- [ ] Hard coded logs path - CHANGE!

Example of S3 file listing:

```
%  aws s3 ls junction-schedules-export/Test/test_data/logs/

2023-05-17 09:20:35       2545 results_2023-05-17T08:20:32.csv
2023-05-17 09:35:25       2545 results_2023-05-17T08:35:22.csv
2023-05-17 09:35:24     120127 results_2023-05-17T08:35:22.html
2023-05-17 10:16:20       2545 results_2023-05-17T09:16:17.csv
2023-05-17 10:16:19     120127 results_2023-05-17T09:16:17.html
```

The `.CSV` summary looks like:

![csv-test-results](/Users/simonh/repos/595-rebase-55/docs/readme-images/csv-test-results.png)

The HTML results are intended to be viewed with a browser, here is the 1st page of a recent results file:

![test-results-html](/Users/simonh/repos/595-rebase-55/docs/readme-images/test-results-html.png)



#### run_all_timeslice

This is the most important test command, it runs the timeslice data preparation and planner, then runs the test against this timeslice planner:

1. Fetch the test data from the S3 bucket (defined in env var `E2E_TEST_YML_FILE`. The script exits if this is not defined or the file cannot be found)
2. Fetch the test data TAR file, as defined above, and expand into `feeds/input_data`
3. Run the data pipeline in 'timeslice' mode, creating one dataset per timeslice.
4. Start `timeslice-planner` with option `start-planners=true`so that a planner instance is started for each timeslice.
5. Run the tests

So this test prepares timeslice data and then runs the timeslice planner against this new data, performing as complete an end to end test as we can devise.

So far results show success for the timeslice planner implementation.

`run_all_timeslice` (and `run_all_classic` below) accept optional parameters:

`-record`

Eg `bash/tests/schedule_tests/run_e2e_tests.sh run_all_timeslice -record`

With this option, for each test run against the planner, the raw planner results are written to a text file, the name is given in the test definition `test-data.known-good-file` and saved in directory `/feeds/known_good/`. When the test run is complete, all files in this directory are saved as a zipped, TAR file and pushed to the S3 path given by the test spec `test-details.known-good-files` (eg see in `s3://junction-schedules-export/Test/test_data/target_test_run.tar.gz`). These files are used for...

`-compare`

The "reverse" of `-record`, the known-good files are downloaded from the S3 path and expanded into `/feeds/known_good/`. As each test is executed, a new (temporary) text file is created from the  Planner results and compared with the previously-saved known-good' file, and if there is any difference, an error is reported. The comparison is a simple line-based diff.

Note that in the test spec, the `test-data.name.results` object is actually optional, so it is possible to define a test with  `from:` `to:` and `afterTime:` values, and simply record a know-good data set (eg perhaps from running the 'classic' monolithic data and planner), then compare future results against this set.

Take care as a `-record` run will overwrite the S3 known-good dataset without warning.

A sample 'KG' file:

```
cat test-1-A-LHR-JFK.txt
{{51.470311 -0.458118 LHR} {40.640556 -73.778519 JFK} 2023-03-01T19:45:00.000+0}
+id: "6b6bf5d9-1896-588c-802a-d948cfe42ba9"
segments: <
  id: "ecc657a4-f57f-5e1b-a9ba-5a4f20814635"
  schedule_id: "8bbfee77-0b01-546a-8333-b08cb9a4a5b1"
  leg_ids: "a9656753-7b81-5e33-927c-d6f8ddea2af9"
>
+id: "7bd1476b-070e-5e21-a89a-f0db51b782a5"
segments: <
  id: "b32094ff-c5db-5ed6-b25d-ffe29e852c1c"
  schedule_id: "d3b31c5c-8e7c-5487-9c1e-416adf97525c"
  leg_ids: "d1c1f8fb-ae7f-5516-9834-a0d40fdf5728"
>
segments: <
  id: "9d61eb7a-68ae-58b5-a2ce-01c4d6228b0b"
  schedule_id: "dba67ddb-b74f-5816-9dd5-61ff696aeaa9"
  leg_ids: "14f4e68b-b789-556c-9c9b-5d3990035e30"
>
```

The KG files are simply text representations of the exact Planner response.

#### run_all_classic

This test is like `run_all_timeslice` but runs the 'classic' (i.e. the current) monolithic data set. The main purpose is to prepare tests for a later timeslice run, or to go back and verify any issues that may arise from timeslice tests. In all other respects the tests are identical, in the test data set up and the output created.



#### run_tests_timeslice, run_tests_classic

These two commands rerun the planner tests but do not recreate the planner datasets. These test run much faster, about 2 - 3 minutes with the tests dataset described above. The test data is downloaded from the S3e bucket , including the test cases, known-good files but not the test-data TAR files. But  `gtfs-import`, and `schedules-export` (or timeslice equivalents) and the mongoDB Loader are NOT run again. The planners are restarted and so reload the existing datasets.

### Docker

The tests are designed to run in a Docker environment to ensure repeatability. The environment is defined in `bash/tests/schedule_tests`and comprises:

`DockerfileE2E` creates a Docker image that will run the tests. It is quite large and comprehensive with Go, Python and many Bash utilities. The default command is `tail -f /dev/null`, i.e. a do-nothing keep-alive. It is intended that users will exec into the instantiated container and run the test commands described above.

`docker-compose.yml` builds a docker environment comprising the E2E container above and a MongoDB container.

`docker-compose.env` defines environment vars that specify the tests to be run, in particular `E2E_TEST_YML_FILE=s3://junction-schedules-export/Test/test_data/target_test.yml` defines the test spec that will be executed. This can be overwritten in the Docker E2E container before running the tests if required to run a different test spec.

README file `bash/tests/schedule_tests/README.md` gives more details.

The docker environment is built with command:

```
  docker compose --file  bash/tests/schedule_tests/docker-compose.yml \
    --env-file bash/tests/schedule_tests/docker-compose.env \
    up  --detach
```

And attached with `docker exec -it e2e-test bash`

(There is a Makefile `bash/tests/schedule_tests/Makefile` which has many useful recipes for running the tests)

###  Slack

When the tests complete, `run_e2e_tests.sh` sends a slack message with a pass or fail message and the S3 path to the test summary. The Slack message is sent using a URL defined in `bash/tests/schedule_tests/docker-compose.env`:

`SLACK_URI=https://hooks.slack.com/services/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`

This url must be created by SRE, the URL defines the Slack channel and authentication. For development only, the URL above sends messages to channel `simon_test` , an example Success message is here:

![slack-message](/Users/simonh/repos/595-rebase-55/docs/readme-images/slack-message.png)

- [ ] @vlado Create new Slack channel and URL.

###  Repos

Currently the test framework is in **Junction** repo , branch `653-time-slice`. It is being managed as a steady feed of MRs until it can be merged into `main`. Currently the branch can be merged into main with no impact, the changes described in _)Changes to the data pipeline and deployment_ must be made to incorporate time-slice data prep and planner use.



## Next Steps

1. Continue the MR process

2. Verify the production-readiness of the timeslice-planner, particularly log monitoring, health server, prometheus etc.

3. Roll out the E2E tests to potential users

4. Implement time-slice planner in dev

5. Test and develop confidence

6. Roll out to prod.


