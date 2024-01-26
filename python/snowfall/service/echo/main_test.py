from snowfall.service.echo import main
from snowfall.service.echo.v1 import echo_pb2
from snowfall.stdlib.transport.grpc import testing


async def test_echo() -> None:
    tester = testing.ServerTester(srv=main.EchoService())

    response = await tester.invoke_unary_unary(
        main.EchoService.Echo,
        echo_pb2.EchoRequest(echo="foobar"),
    )

    assert response.message.echo == "foobar"
