# Ports

This file is mainly meant as a way to keep track on which services are running on
which ports during local development.

## Default Ports

The following ports should be used as default for various network protocols and
services. Please note that ports must always be configurable through environment
variables.

| Port  | Description |
| :---: | :---------- |
|  80   | HTTP Server |
| 50051 | gRPC Server |

## Port Assignments

The following ports are configured in local environments by default:

| Port  | Service                | Description |
|:-----:|:-----------------------| :---------- |
| 8000  | client-api             | HTTP Server |
| 8001  | mobile-api             | HTTP Server |
| 8003  | pay-api                | HTTP Server |
| 8004  | dogfood-ui             | HTTP Server |
| 8006  | pay-admin-api          | HTTP Server |
| 8007  | data-api               | HTTP Server |
| 8008  | webhooks               | HTTP Server |
| 8009  | hub/web-api            | HTTP Server |
| 8010  | plus/webhooks          | HTTP Server |
| 8011  | zendesk_webhook        | HTTP Server |
| 8012  | plus-api               | HTTP Server |
| 8013  | rocket-dogfood-ui      | HTTP Server |
| 50051 | echo                   | gRPC Server |
| 50052 | places                 | gRPC Server |
| 50053 | planner                | gRPC Server |
| 50054 | trips                  | gRPC Server |
| 50055 | offers                 | gRPC Server |
| 50056 | schedules              | gRPC Server |
| 50057 | orders                 | gRPC Server |
| 50058 | geodata                | gRPC Server |
| 50059 | passenger-name-records | gRPC Server |
| 50060 | currencies             | gRPC Server |
| 50061 | payers                 | gRPC Server |
| 50062 | authentication         | gRPC Server |
| 50063 | checkin                | gRPC Server |
| 50064 | accounts               | gRPC Server |
| 50065 | gateway                | gRPC Server |
| 50066 | mock                   | gRPC Server |
| 50067 | payments               | gRPC Server |
| 50068 | ask2go                 | gRPC Server |
| 50069 | ba-ndc                 | gRPC Server |
| 50070 | direct_ferries         | gRPC Server |
| 50071 | distribusion           | gRPC Server |
| 50072 | duffel                 | gRPC Server |
| 50073 | save-a-train           | gRPC Server |
| 50074 | transactions           | gRPC Server |
| 50075 | companies              | gRPC Server |
| 50076 | notifications          | gRPC Server |
| 50077 | refunds                | gRPC Server |
| 50079 | resellers              | gRPC Server |
| 50080 | co2 emissions          | gRPC Server |
| 50081 | karhoo                 | gRPC Server |
| 50082 | carnect                | gRPC Server |
| 50083 | content/benerail       | gRPC Server |
| 50085 | content/ask2go         | gRPC Server |
| 50086 | content/direct_ferries | gRPC Server |
| 51051 | rocket/searches        | gRPC Server |
| 51052 | rocket/gateway         | gRPC Server |
| 51053 | rocket/mock            | gRPC Server |
| 51054 | rocket/carnect         | gRPC Server |
| 51055 | rocket/places          | gRPC Server |
| 51056 | rocket/bookings        | gRPC Server |
| 51057 | rocket/direct_ferries  | gRPC Server |
| 51058 | rocket/benerail        | gRPC Server |
| 51059 | rocket/silverrail      | gRPC Server |
