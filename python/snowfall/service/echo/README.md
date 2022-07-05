---
internal: true
---

# Echo Service
This is an example service that uses grpc.

When it receives an Echo protobuf message, it echoes it back to the sender.

Find the protobuf messages it supports in:

```
protobuf/snowfall/service/echo/v1/echo.proto
```

Run it by using the instructions in the root README.md or CONTRIBUTING.md file.

## Example usage:

```
python main.py grpc
grpcurl -plaintext -d "{\"echo\": \"hello\"}" localhost:50051 snowfall.project.junction.service.echo.v1.EchoService/Echo
```

## Prerequisites:
Can be installed using `brew` or any other package manager.
```
grpcurl
```
