import re

FILTERED_WORD = "[Filtered]"
SECRET_WORDS: tuple[str, ...] = (
    "AggregatorID",
    "AgencyID",
    "IATA_Number",
    "CardNumber",
    "SeriesCode",
)


class LogFilter:
    def __init__(
        self,
        secret_words: tuple[str, ...] | None = SECRET_WORDS,
        filtered_word: str = FILTERED_WORD,
    ):
        self._search_re: re.Pattern[str] | None = None
        self._replace_re: str | None = None

        if secret_words:
            ns = r"(?:\w{1,6}:)?"
            fields = "|".join([re.escape(vi) for vi in secret_words])
            search_re = r"(<({ns}(?:{fields}))[^>]*>)[^<]+(</\2>)".format(
                ns=ns,
                fields=fields,
            )
            self._search_re = re.compile(search_re, re.DOTALL)
            self._replace_re = r"\1{filtered_word}\3".format(
                filtered_word=filtered_word,
            )

    def log_filter(
        self,
        log_data: str | bytes | None,
        charset: str = "utf-8",
    ) -> str | None:
        if log_data:
            if isinstance(log_data, bytes):
                vi = log_data.decode(encoding=charset if charset else "utf-8")
            else:
                vi = log_data

            if self._search_re is not None and self._replace_re:
                return self._search_re.sub(self._replace_re, vi)

            return vi

        return None
