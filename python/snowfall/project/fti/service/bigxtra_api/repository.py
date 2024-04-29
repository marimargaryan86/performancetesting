from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class Repository:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self._session_maker = session_maker

    async def find_places(self, destination: str | None) -> dict[str, Any]:
        return {"places": []}
