from typing import Any, ClassVar

from snowfall.stdlib.logging import stdout


class AIBot(object):
    system_setup = "You are an AI travel assistant"
    functions: ClassVar[Any] = []

    def __init__(self) -> None:
        self._logger = stdout.get_logger()

    async def handle_prompt(self, message: str) -> None:
        """Get message history from state, append message and send to openai."""
