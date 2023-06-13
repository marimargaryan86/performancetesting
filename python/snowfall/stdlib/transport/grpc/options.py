from collections.abc import Iterable
from typing import cast

from google.protobuf import descriptor, message
from grpc import aio

from snowfall.stdlib.transport.grpc import interceptor

_Field = tuple[descriptor.FieldDescriptor, message.Message | Iterable[message.Message]]


def clear_message_with_option(msg: message.Message, option_name: str) -> None:
    for field in msg.ListFields():
        for option in field[0].GetOptions().ListFields():
            if option[0].name == option_name and option[1]:
                msg.ClearField(field[0].name)
                break
        else:
            _clear_nested_message_with_option(field, option_name)


def _clear_nested_message_with_option(
    field: _Field,
    option_name: str,
) -> None:
    message_type: descriptor.Descriptor | None = field[0].message_type

    if message_type:
        if field[0].label == descriptor.FieldDescriptor.LABEL_REPEATED:
            for field_value in cast(Iterable[message.Message], field[1]):
                clear_message_with_option(field_value, option_name)
        else:
            clear_message_with_option(cast(message.Message, field[1]), option_name)


class OptionsInterceptor(interceptor.ServerInterceptor):
    async def intercept_unary_unary(
        self,
        continuation: interceptor.UnaryUnary,
        request: message.Message,
        context: aio.ServicerContext,
    ) -> message.Message:
        clear_message_with_option(request, "read_only")

        response = await continuation(request, context)

        clear_message_with_option(response, "write_only")

        return response
