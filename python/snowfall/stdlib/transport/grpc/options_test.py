from snowfall.stdlib.transport.grpc import options
from snowfall.stdlib.v1 import testing_pb2


def test_clear_message_with_option() -> None:
    proto = testing_pb2.Foobar(read_only="test")

    assert proto.read_only == "test"
    options.clear_message_with_option(proto, "read_only")
    assert proto.read_only != "test"


def test_clear_message_with_option_nested() -> None:
    proto = testing_pb2.Foobar(nested_foobar=testing_pb2.Foobar(write_only="test"))

    assert proto.nested_foobar.write_only == "test"
    options.clear_message_with_option(proto, "write_only")
    assert proto.nested_foobar.write_only != "test"


def test_clear_message_with_option_repeated() -> None:
    proto = testing_pb2.RepeatedFoobar(foobars=[testing_pb2.Foobar(write_only="test")])

    assert proto.foobars[0].write_only == "test"
    options.clear_message_with_option(proto, "write_only")
    assert proto.foobars[0].write_only != "test"
