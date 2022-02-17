# Ports

This file is mainly meant as a way to keep track on which services are running on
which ports during local development.

## Default Ports

The following ports should be used as default for various network protocols and
services. Please note that ports must always be configurable through environment
variables.

| Port  | Description       |
| :---: | :---------------- |
| 80    | HTTP Server       |
| 8080  | Prometheus Server |
| 50051 | gRPC Server       |

## Port Assignments

The following ports are configured in local environments by default:

| Port  | Service    | Description |
|:----: | :--------- | :---------- |
| 8000  | client-api | HTTP Server |
| 50051 | echo       | gRPC Server |
| 50052 | places     | gRPC Server |
| 50053 | planner    | gRPC Server |
| 50054 | trips      | gRPC Server |

