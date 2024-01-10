import antlr4

from snowfall.stdlib.format.filter_parser import (
    FilterLexer,
    FilterParser,
)


def parse(filter_: str) -> FilterParser.FilterParser.FilterContext:
    lexer = FilterLexer.FilterLexer(antlr4.InputStream(filter_))
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = FilterParser.FilterParser(token_stream)

    return parser.filter_()
