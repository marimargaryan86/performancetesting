from collections.abc import Sequence
from datetime import date
from typing import Any

from sqlalchemy import Column, ForeignKey, func, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    def key(self) -> None:
        return


class Availabilities(Base):
    __tablename__ = "availabilities"

    id: Mapped[str] = mapped_column(primary_key=True)
    accommodation: Mapped["Accommodations"] = relationship(
        back_populates="availabilities",
    )
    accommodation_id: Mapped[str] = mapped_column(ForeignKey("accommodations.id"))
    month: Mapped[date]
    unit: Mapped[str]
    default: Mapped[int]
    exceptions = Column(JSONB)


class PriceItems(Base):
    __tablename__ = "price_items"

    id: Mapped[str] = mapped_column(primary_key=True)
    accommodation: Mapped["Accommodations"] = relationship(back_populates="price_items")
    accommodation_id: Mapped[str] = mapped_column(ForeignKey("accommodations.id"))
    unit: Mapped[str]
    date: Mapped[date]
    duration: Mapped[int]
    board: Mapped[str]
    price: Mapped[float]


class Occupancy(Base):
    __tablename__ = "occupancy"

    id: Mapped[str] = mapped_column(primary_key=True)
    accommodation: Mapped["Accommodations"] = relationship(back_populates="occupancy")
    accommodation_id: Mapped[str] = mapped_column(ForeignKey("accommodations.id"))
    unit: Mapped[str]
    occupancy: Mapped[str]


class Accommodations(Base):
    __tablename__ = "accommodations"

    id: Mapped[str] = mapped_column(primary_key=True)
    price_items: Mapped[list["PriceItems"]] = relationship(
        back_populates="accommodation",
        cascade="all, delete-orphan",
    )
    availabilities: Mapped[list["Availabilities"]] = relationship(
        back_populates="accommodation",
        cascade="all, delete-orphan",
    )
    occupancy: Mapped[list["Occupancy"]] = relationship(
        back_populates="accommodation",
        cascade="all, delete-orphan",
    )


class Repository:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self._session_maker = session_maker

    async def find_places(self, destination: str | None) -> dict[str, Any]:
        return {"places": []}

    async def check_availability(
        self,
        checkin: date,
        duration: int,
        occupancy: str,
    ) -> Sequence[Any]:
        async with self._session_maker() as sess:
            stmt = (
                select(
                    Occupancy.accommodation_id,
                    func.array_agg(Occupancy.unit),
                )
                .where(Occupancy.occupancy == occupancy)
                .group_by(
                    Occupancy.accommodation_id,
                )
            )
            result = await sess.execute(stmt)
            accommodation_result = result.all()

            for res in accommodation_result:
                for unit in res[1]:
                    stmt = select(
                        Availabilities.default,
                        Availabilities.exceptions,
                    ).where(
                        Availabilities.unit == unit,
                        Availabilities.accommodation_id == res[0],
                        Availabilities.month == checkin.replace(day=1),
                    )
                    result = await sess.execute(stmt)
                    availability_result = result.first()
                    if not availability_result:
                        res[1].remove(unit)  # noqa: WPS220
            return accommodation_result

    async def get_price_item(
        self,
        checkin: date,
        duration: int,
        accommodation_id: str,
        unit: str,
    ) -> PriceItems | None:
        async with self._session_maker() as sess:
            stmt = select(PriceItems).where(
                PriceItems.date == checkin,
                PriceItems.duration == duration,
                PriceItems.accommodation_id == accommodation_id,
                PriceItems.unit == unit,
            )
            result = await sess.execute(stmt)
            return result.scalar()
