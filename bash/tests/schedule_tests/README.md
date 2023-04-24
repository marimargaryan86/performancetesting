# Schedules E2E Tests



`tests/schedule_tests/README.md`



## related files

Tests are run by `tests/schedule_tests/run_e2e_tests.sh`

Which is run in the CI Pipeline by `.gitlab/planner-test.gitlab-ci.yml`



## Test Files

There are several types of  "test file", all are retrieved from an S3 bucket at test runtime

* A test YML file containing one or more test requests and the expected results (See Appendix A). This file is downloaded first, and must have field `gtfs-tar-file: ` which is the S3 path to...
* A tar file with test data used by the Planner
* And optionally the test YML file may name a "known-good" results file for a `-compare` run (see below)



Each test YML file may be for a different test purpose (use the `name:` and `comment:` fields to describe the tests). Each YML file must identify a data TAR file, but many test YML files may use the same TAR file e.g. they are running different tests on the same dataset.

The test runner `tests/schedule_tests/run_e2e_tests.sh` expects environment variable `E2E_TEST_YML_FILE`to be the full S3 path to a test YML file, including the S3 bucket, such as: `s3://junction-schedules-export/Test/test_data/quick_test.yml`





This S3 directory has the static test data for the Schedules End to End tests. These comprise:

| Purpose         | Example Filename                              | Type    | Comment                                        |
| --------------- | --------------------------------------------- | ------- | ---------------------------------------------- |
| Test directory  | S3://junction-schedules-export/Test/test_data | S3 path |                                                |
| Tests GTFS data | `e2e_test_data.tar`                           | TAR     | A number of GTFS files used for every E2E test |

Push:

**NB Make sure there are no PATHS in the .tar file**

So create the tar file IN the directory with the zip files.

```
cd /feeds/test_data
% tar -cvf e2e_test_data.tar test_data/*.zip
% aws s3 cp e2e_test_data.tar s3://junction-schedules-export/Test/test_data/e2e_test_data.tar
% aws s3 ls s3://junction-schedules-export/Test/test_data/
2023-02-13 14:07:30    4221440 e2e_test_data.tar
% shasum *tar
88e152a97142975df1266909f5d41d6b0ccccec0  e2e_test_data.tar
```

Run the test setup with

`/junction/tests/schedule_tests/run_e2e_tests.sh `

Run the tests themselves with

```
cd golang
go run cmd/planner-test-client/planner-test-client.go -- -test-file=/junction/golang/cmd/planner-test-client/test.yml

```



I know a tar of zipped files will not save space! Just creating a single archive.

Files:

| FileName    | Provider                                    | Size |
|-------------|---------------------------------------------|--|
| ssim-tk     | Turkish Airlines Inc.                       | 907 kb |
| ssim-lx     | SWISS International Air Lines Ltd dba SWISS | 485 Kb |
| OBB.zip     | Austrian Railways                           | 2400 kb |
| ssim-a3.zip | Aegean|381 kb|
| Ferry ??? | Xxxx ||
| OUTPUT      | tests/schedule_tests/e2e_test_data.tar      | 3,121 kb |



## Environment Variables

These env vars must be set for the test to run

| Env Var           | Purpose                                         | Example                                                      |
| ----------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| E2E_TEST_YML_FILE | S3 path to a test YAML file (see above)         | s3://junction-schedules-export/Test/test_data/test.yml       |
| E2E_DATA_ROOT     | Directory path for all the Planner related data | /feeds                                                       |
| MONGODB           | URI of the MongoDB to use                       | mongodb://mongo-db:27017 (this is the Docker Compose service name) |
|                   |                                                 |                                                              |

Note these values are set in `tests/schedule_tests/docker-compose.env` and used by `docker compose` as:

```
    docker compose --file  tests/schedule_tests/docker-compose.yml \
        --env-file tests/schedule_tests/docker-compose.env \
        up --build --detach
```

Although this is specific to local running and will change for production pipeline running.

### Notes

Lookup 2-character Airline codes [iata](https://www.iata.org/en/publications/directories/code-search/?airline.search=tk])

## Docker Compose



### Why have we configured the Docker images this way?

The Docker Compose file is `tests/schedule_tests/DockerfileE2E`. It creates two Containers

* e2e-mongo, which runs the MongoDB database
* e2e-test, which runs the end to end tests

Now to run the tests, e2e-test needs:

* Python (3.9)
* Go (golang)
* MongoDB database tools
* Pants



As I am developing on an M1 macBook, then we need everything installed to be ARM compatible

The MongoDB database tools ONLY run on Ubuntu:20.04 (or earlier, but not latest 22), so the Dockerfile `tests/schedule_tests/DockerfileE2E` starts with `FROM ubuntu:20.04`

```
NB (really bene) Cannot install mongodb-database-tools on Debian on ARM64,
see https://www.mongodb.com/try/download/database-tools, https://www.mongodb.com/try/download/database-tools OK
https://www.mongodb.com/try/download/database-tools OK, Debian/ARM64 NO
```

The rest of this Dockerfile is to install these dependencies.

**Why run mongorestore from e2e-test?**

It would make a lot of sense to run `mongorestore` on the e2e-mongo` container, but how? ``e2e-test` builds all the data including the `.bson` files needed to run `mongoorestore`, so it must initiate the action.

From a MacBook or PC terminal, we would simply run something like: `docker run -it e2e-test mongorestore <parameters...>`  But to run this from a Docker container, requires docker-in-docker, to be avoided if possible.

We could use `SSH` to run a remote command. To do this, we need to create a new Dockerfile to create a custom image starting with `FROM mongo` , add the ssh daemon and create a user to receive the SSH call. However the Mongo image does not have  `systemd` or any other system controller - so there is no way to start the SSH daemon when the container is instantiated! (Manually starting the Daemon allows this method to work well). So we could start from a basic Ubuntu, install Mongo and SSH, but adding Mongo Tools to `e2e-test` looks simpler.



# Planner Tester 'Known Good' tests



## Intro

Goran requested that the planner tester suite can also do "Known Good" tests, as follows:

1. Keep the existing `test.yml` file, `input` section, which describes the request to be sent to the Planner service.
2. Run a 'Known good' run, and for each Planner response received, save as a human-readable file
3. Subsequently, run a 'diff' test. Make the same planner requests, but now compare the Planner request with the saved file (in human-readable form). If there is any difference, list it as an error.

(_KG_ is used as an abbreviation for known-good.)

### Requirements

So the elements we need are:

1.  Some means of telling the planner tester `planner-test-client.go` whether it is running in *record* or *compare* mode.
2.  A location to save the files and a naming convention.
3.  A way to save and restore these files between runs, using S3.

### Solution

1.  A program CLI options will be used, `-compare` or `-record` (or neither).
2.  `-compareFile` overrides the S3 path to the KG tar file (specified in `test.yml` at `test-details:known-good-files`)

If  `-compare` or `-record` are specified, the 'conventional' tests will not be performed. To run the 'conventional' tests, omit  `-compare` and `-record`

## Use Instructions

From the repo root, the tests can be run in Docker using

```bash
    docker compose --file  tests/schedule_tests/docker-compose.yml \
        --env-file tests/schedule_tests/docker-compose.env \
        up --build --detach
```

Set the values in `docker-compose.env` to determine the run:
```
E2E_TEST_YML_FILE=s3://junction-schedules-export/Test/test_data/kg_test.yml
```

* `SLACK_URI` to the URI for the desired Slack channel (see @vlado to set this up)

* `KG_RUN_TYPE` : Omit for 'full' tests only. `-record` to create a new recording of known-good file. `-compare` to test against a previously known-good file.

* `RUN_DATE` The date to be used in creating the test data, `yyyy:mm:dd` only

And note that the test data archive and the known-good file archive are both specified in the tests.yml file.

### **Naming convention:**

**test.yml**

Two new fields will be added to the `test.yml` file:

**known-good-files**

`test-details:known-good-files` is the S3 path to a tar file of zero or more "known good files" such as : `known-good-files: s3://junction-schedules-export/Test/test_data/basic_test_run.tar.gz`. On a `-record` run, a new tar file is created, the creation datestamp added and uploaded to the S3 (such as `s3://junction-schedules-export/Test/test_data/basic_test_run_2023-02-07T17:20:00Z.tar.gz`).

For a `-compare` run, since the `test.yml` `test-details:known-good-files` does not include a timestamp, the latest file matching the path is used. To run a specific results set, use the `-compareFile` flag eg:

`-compareFile=s3://junction-schedules-export/Test/test_data/basic_test_run_2023-02-07T17:20:00Z.tar`. If no such file exists, the test run exits with a negative error code (as positive error codes indicate the number of test failures).

If this flag is used for a `-record` run, the results will be uploaded to exactly this path.

Note the program does not manage the number of such files in the S3 bucket, any housekeeping must be done manually.

**known-good-file**

New field`test-data:known-good-file` is added for each test case that is participating in the known good tests. It must contain a  name that is unique to the test yml file. This is the filename prefix for the KG file, with extension  `.dat` . Spaces are stripped from the filename, so

`known-good-file: test 1 BA183` will produce a filename `test_1_BA183.dat`

Not every test case has to have this value. Each test case may have either a `known-good-file` section or a `results` section OR BOTH.

These files are used to create the `.tar.gz` file in `-record`, and extracted from the same `.tar.gz` for a `-comopare` operation.

### Files and Directories

**Known Good Files**

The Known Good file will be dumped from the protobuf messages received from the gRPC _planner_ call,  See the example in Appendix B.

The files will be saved in the `feeds` directory at `feeds/known-good`, (`/feeds/known-good` in a Docker container).   At the end of a `-record` run, the files are compressed into a TAR file and uploaded, as described above.

For a `-compare` run, the files are downloaded and extracted before the test run starts.

The tar files is created with `tar -cz` to create a zipped tar file, named `feeds/known-good/known-good-routes_<datestamp>.tar.gz`

#### Notes

The two types of test are effectively independent.

## Reports

Two report types may be produced.

#### Full test report

For a 'full' test, a detailed report is produced listing:

* The test run details
* Each test case:
  * The test case details, i.e. the from/to and after-time values
  * The routes actually found by the planner.
  * The results of checking these results against the expected test results
* A summary of total and passed test-cases and tests.

This report is uploaded to the S3 bucket as `results_<timestamp>`, in two forms, `.html` and `.pdf`

(Note - HTML is easier to create using Go package `html/format`, and looks better, it is converted to PDF by command line tool `weasyprint` (_qv_). We may want to drop one format?)

#### Known Good test report

This is a much smaller `.txt` Text file, listing each test case and the comparisons with the prior 'known-good' data, either **PASS** or a **FAIL** with the FIRST difference listed. See Appendix C.

Samples of these reports are in `Google Drive` [here](https://drive.google.com/drive/folders/1qU0W-nf3czOfgZNu7qupSZs9WqZ-TMG6?usp=share_link) (sample HTML, PDF and TXT files)





#### Test Program Exit Code

The program `golang/cmd/planner-test-client/planner-test-client.go` exits with:

* 0 if all tests passed, or
* A +ve number, being the number of tests that failed, or
* A -ve number if there is a program failure



The shell script `tests/schedule_tests/run_e2e_tests.sh` exits with the same codes.

Thus the script can be included in a pipeline, and test success/failure determined from the exit code.

##### Slack notification

When the test run completes, a Slack notification is raised, with the success of failure status and the S3 path to the report, like:

```
Vlado_Grafana_Alert_Test
APP  3:03 PM
planner-test-client.go PASSED results in s3://junction-schedules-export/Test/test_data/logs/results_2023-03-13T15:03:44.html
```

The slack channel and authentication is from the Env Var `SLACK_URI`, development example:

```
SLACK_URI=https://hooks.slack.com/services/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
```

This path specifies the Slack channel (`Vlado_Grafana_Alert_Test` in this case), and contains the authentication keys. See @vlado to get a different Slack path.

------

# Appendices

## Appendix A - sample test.yml file

```
---
test-details:
  name: Basic test run
  created-date: 2023-02-07T17:20:00Z
  created-by: Simon Hewitt
  gtfs-tar-file: s3://junction-schedules-export/Test/test_data/e2e_test_data.tar
  gtfs-tar-sha1: 6f3eb536de0779cb653b72daef624653a0dbdfe7
  known-good-files: s3://junction-schedules-export/Test/test_data/basic_test_run.tar.gz
  comment: Version 1 POC
test-data:
  - name: test 1 (later) BA183 LHR JFK 2023-03-01T19:45:0019:45
    known-good-file: test 1 BA183
    skip: false
    input:
      from:
        Latitude: 51.470311
        Longitude: -0.458118
        name: LHR
      to:
        Latitude: 40.640556
        Longitude: -73.778519
        name: JFK
      afterTime: 2023-03-01T19:45:00.000+0
      known-good-file: test-1
    results:
      - testName: BA183 direct
        segments:
          - name: BA183
            agencyName: BA
            transportMode: air
            operator: Aegean
            numberOfLegs: 1
            legs:
              - operationNumber: A3-609
                departure: Heathrow Airport
                departureTime: 19:45:00
                arrival: JFK
                arrivalTime: 03:45:00
      - testName: TK1984 & TK3
        segments:
          - name: TK1984
            agencyName: TK
            transportMode: air
            operator: Aegean
            numberOfLegs: 1
            legs:
              - operationNumber: A3-609
                departure: Heathrow Airport
                departureTime: 22:35:00
                arrival: IST
                arrivalTime: 02:15:00
          - name: TK3
            agencyName: TK
            transportMode: air
            operator: Aegean
            numberOfLegs: 1
            legs:
              - operationNumber: A3-609
                departure: Istanbul Airport
                departureTime: 05:50:00
                arrival: JFK
                arrivalTime: 16:50:00
  - name: test 1-2 (earlier)BA183 LHR JFK
    known-good-file: test 1-2 BA183
    skip: false
    input:
      from:
        Latitude: 51.470311
        Longitude: -0.458118
        name: LHR
      to:
        Latitude: 40.640556
        Longitude: -73.778519
        name: JFK
      afterTime: 2023-03-01T19:45:00.000+0

```



## Appendix B - Sample KG file

A sample "Known Good" file "test 1-A.txt":

```
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

The first line is a dump of the test input:

```
{{from-lat, from-lon, from-name} {to-lat to-lon to-name} {after-utc-time}}
```

The rest of the. File details the route(s) returned by the planner. Each "+" marks the start of a new route, with the schedule ID and the list of one or more segments inside the "<>" chevrons.

As the 'Known-Good' and test run results are directly compared as slices of strings, do not touch the format unless necessary! If the format is changed, it will be necessary to execute a new `-record` run.

## Appendix C - Known Good Comparison report

```
**Planner Test Report**

Test Run Details

Name:                   Simple record/compare Known Good test
Version:                Version 1 demo
Test YML file:          /feeds/input_data/kg_test.yml
Data TAR file:          s3://junction-schedules-export/Test/test_data/e2e_test_data.tar
"Known-Good" TAR file:
Run time (Wall Clock Time): 2023-03-13 11:40:30

Summary:
    Total test cases :  3, passed: 3 (100.00%)
    Total tests :       3, passed: 3 (100.00%)
    test Exit Code:     0


  Test Case name:   test 1-A BA183 LHR JFK 2023-03-07
  Skip? :           false
  Passed? :         true
  Test Count :      1  Tests Passed: 1
  Known Good File:  test 1-A-LHR-JFK
  Known Good Errors:

  Test Case name:   test 1-B BA183 LHR JFK 2023-03-01
  Skip? :           false
  Passed? :         true
  Test Count :      1  Tests Passed: 1
  Known Good File:  test 1-B-LHR-JFK
  Known Good Errors:

  Test Case name:   test 2 Tallinn to Istanbul on TK
  Skip? :           false
  Passed? :         true
  Test Count :      1  Tests Passed: 1
  Known Good File:  test 2-TLL->IST
  Known Good Errors:
```

## Appendix D - sample test report

Can be seen in the repo at `tests/schedule_tests/results_2023-03-13T13:46:12.pdf`



[sample report](file:///results_2023-03-13T13:46:12.pdf)

## Appendix E - History

| Version | Date    | Author       | Purpose                                  |
| ------- | ------- | ------------ | ---------------------------------------- |
| 0.1     | 2/3/23  | Simon Hewitt | 1st draft                                |
| 1.0     | 9/3/23  | Simon Hewitt | 1st release                              |
| 1.1     | 13/3/23 | Simon Hewitt | Added 'instructions'                     |
| 1.2     | 15/3/23 | Simon Hewitt | Merged two markdown files into readme.md |





