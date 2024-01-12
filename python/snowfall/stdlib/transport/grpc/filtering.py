import functools

import antlr4
from google.protobuf import descriptor

from snowfall.stdlib.format import dsl
from snowfall.stdlib.format.filter_parser import FilterListener, FilterParser


class InvalidFilterError(Exception):
    """Raised when a filter is invalid."""


@functools.cache
def _validate_member(msg: descriptor.Descriptor, member: str) -> None:
    for field_name in member.split("."):
        try:
            field = msg.fields_by_name[field_name]
        except AttributeError:
            raise InvalidFilterError(
                '"{0}" is not a nested field'.format(field_name),
            ) from None
        except KeyError:
            raise InvalidFilterError(
                '"{0}" is not a valid field'.format(field_name),
            ) from None

        msg = field.message_type


class _Validator(FilterListener.FilterListener):
    def __init__(self, msg: descriptor.Descriptor) -> None:
        self._msg = msg

    def enterMember(self, ctx: FilterParser.FilterParser.NameContext) -> None:  # noqa: N802
        _validate_member(self._msg, ctx.getText())


def parse(
    msg: descriptor.Descriptor,
    filter_: str,
) -> FilterParser.FilterParser.FilterContext:
    try:
        tree = dsl.parse_filter(filter_)
    except dsl.ParseError as err:
        raise InvalidFilterError(str(err)) from err

    antlr4.ParseTreeWalker().walk(_Validator(msg), tree)

    return tree
