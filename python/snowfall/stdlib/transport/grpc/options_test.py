from google.protobuf import struct_pb2

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


def test_clear_message_with_struct() -> None:
    some_struct = struct_pb2.Struct()
    some_struct.update({"foo": "bar"})
    proto = testing_pb2.Foobar(struct=some_struct)

    options.clear_message_with_option(proto, "read_only")
    assert proto.struct["foo"] == "bar"


def test_read_only_struct_is_cleared() -> None:
    some_struct = struct_pb2.Struct()
    some_struct.update({"foo": "bar"})
    proto = testing_pb2.Foobar(read_only_struct=some_struct)

    assert proto.read_only_struct
    options.clear_message_with_option(proto, "read_only")
    assert not proto.read_only_struct


def test_clear_message_with_map() -> None:
    proto = testing_pb2.Foobar(map={"foo": "bar"})

    options.clear_message_with_option(proto, "read_only")
    assert proto.map["foo"] == "bar"


def test_read_only_map_is_cleared() -> None:
    proto = testing_pb2.Foobar(read_only_map={"foo": "bar"})

    assert proto.read_only_map
    options.clear_message_with_option(proto, "read_only")
    assert not proto.read_only_map
