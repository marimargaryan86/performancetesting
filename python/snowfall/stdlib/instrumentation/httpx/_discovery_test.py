import inspect

from snowfall.stdlib.instrumentation.httpx import _discovery  # noqa: PLC2701


class TestDiscovery:
    def test_correct_calling_name(self) -> None:
        assert _discovery.get_calling_method() == inspect.stack()[0].function

    def test_correct_parent_class(self) -> None:
        assert _discovery.get_parent_class() == self.__class__.__name__
