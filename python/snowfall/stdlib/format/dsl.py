import dataclasses
from typing import Any, NoReturn

import antlr4
from antlr4.error import ErrorListener
from antlr4.Token import CommonToken

from snowfall.stdlib.format.filter_parser import (
    FilterLexer,
    FilterParser,
)


@dataclasses.dataclass(frozen=True)
class ParseError(Exception):
    column: int
    line: int
    message: str

    def __str__(self) -> str:
        return "Unable to parse line {line} column {column}: {message}".format(
            column=self.column,
            line=self.line,
            message=self.message,
        )


class _ErrorListener(ErrorListener.ErrorListener):
    def syntaxError(  # noqa: N802
        self,
        recognizer: FilterParser.FilterParser,
        offendingSymbol: CommonToken,  # noqa: N803
        line: int,
        column: int,
        msg: str,
        e: Any,  # noqa: WPS111
    ) -> NoReturn:
        super().syntaxError(
            recognizer=recognizer,
            offendingSymbol=offendingSymbol,
            line=line,
            column=column,
            msg=msg,
            e=e,
        )

        raise ParseError(column=column, line=line, message=msg)


def parse_filter(filter_: str) -> FilterParser.FilterParser.FilterContext:
    lexer = FilterLexer.FilterLexer(antlr4.InputStream(filter_))
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = FilterParser.FilterParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(_ErrorListener())

    return parser.filter_()
