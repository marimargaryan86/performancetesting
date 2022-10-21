---
internal: true
---

# Ports

This file is mainly meant as a way to keep track on which services are running on
which ports during local development.

## Default Ports

The following ports should be used as default for various network protocols and
services. Please note that ports must always be configurable through environment
variables.

| Port  | Description       |
|:-----:|:------------------|
|  80   | HTTP Server       |
| 50051 | gRPC Server       |

## Port Assignments

The following ports are configured in local environments by default:

| Port  | Service                | Description       |
|:-----:|:-----------------------|:------------------|
| 8000  | client-api             | HTTP Server       |
| 8001  | mobile-api             | HTTP Server       |
| 8002  | admin-api              | HTTP Server       |
| 8003  | pay-api                | HTTP Server       |
| 8004  | dogfood-ui             | HTTP Server       |
| 50051 | echo                   | gRPC Server       |
| 50052 | places                 | gRPC Server       |
| 50053 | planner                | gRPC Server       |
| 50054 | trips                  | gRPC Server       |
| 50055 | offers                 | gRPC Server       |
| 50056 | schedules              | gRPC Server       |
| 50057 | orders                 | gRPC Server       |
| 50058 | geodata                | gRPC Server       |
| 50059 | passenger-name-records | gRPC Server       |
| 50060 | currencies             | gRPC Server       |
| 50061 | payers                 | gRPC Server       |
