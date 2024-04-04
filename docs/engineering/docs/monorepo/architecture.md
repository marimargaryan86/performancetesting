---
sidebar_position: 3
---

# Architecture

The main architectural pattern that we follow in Junction is a
microservice-based architecture with [gRPC](https://grpc.io/) for synchronous
communication between services, and [RabbitMQ](https://www.rabbitmq.com/) for
asynchronous communication (message passing). Protobufs are used for most data
serialization (service communication as well as data persistence).

Services exposed to the internet have a REST JSON API, which we specify with
[OpenAPI](https://www.openapis.org/).  For consistency, the REST APIs follow
the [JSON:API](https://jsonapi.org/) style.

Our data persistence layer is mainly [MongoDB](https://www.mongodb.com/), but we also
use [Redis](https://redis.io/).

The Junction architecture overview can be found on a [miro
whiteboard](https://miro.com/app/board/uXjVOIhsVCg=/).
