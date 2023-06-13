import re

FILTERED_WORD = "[Filtered]"
SECRET_WORDS: tuple[str, ...] = (
    "AggregatorID",
    "AgencyID",
    "IATA_Number",
    "CardNumber",
    "SeriesCode",
)


class LogFilter(object):
    def __init__(
        self,
        secret_words: tuple[str, ...] | None = SECRET_WORDS,
        filtered_word: str = FILTERED_WORD,
    ):
        self._search_re: re.Pattern[str] | None = None
        self._replace_re: str | None = None

        if secret_words:
            ns = "(?:\\w{1,6}:)?"  # noqa: WPS342
            fields = "|".join([re.escape(vi) for vi in secret_words])
            search_re = (
                "(<({ns}(?:{fields}))[^>]*>)[^<]+(</\\2>)".format(  # noqa: WPS342
                    ns=ns,
                    fields=fields,
                )
            )
            self._search_re = re.compile(search_re, re.DOTALL)
            self._replace_re = "\\1{filtered_word}\\3".format(  # noqa: WPS342
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
