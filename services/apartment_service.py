# Здесь скрипт принимает сформированный запрос что выбрать с базы, подключается к базе через database.database и выбирает то что нужно Если фильтров нет то отправляет последние 20 объектов

from sqlalchemy import desc, and_  # добавь это
from sqlalchemy.future import select
from models.apartment import Apartment
from database.database import async_session

"""async def get_apartments(limit: int = 10000, offset: int = 0):
    async with async_session() as session:
        query = select(Apartment).order_by(desc(Apartment.ID)).limit(limit).offset(offset)
        result = await session.execute(query)
        apartments = result.scalars().all()
        return apartments"""


async def get_apartments(skip: int = 0, limit: int = 20, filters: dict = None):
    async with async_session() as session:
        query = select(Apartment).order_by(desc(Apartment.ID))
        conditions = []

        if filters:
            if filters.get("Activity"):
                conditions.append(Apartment.Activity == filters["Activity"])
            if filters.get("RealityType"):
                conditions.append(Apartment.RealityType == filters["RealityType"])
            if filters.get("RegionID"):
                conditions.append(Apartment.RegionID == filters["RegionID"])
            if filters.get("DistrictId"):
                conditions.append(Apartment.DistrictId == filters["DistrictId"])
            if filters.get("PragueLocalityId"):
                prague_ids = filters["PragueLocalityId"]
                if isinstance(prague_ids, list):
                    conditions.append(Apartment.PragueLocalityDI.in_(prague_ids))
                else:
                    conditions.append(Apartment.PragueLocalityDI == prague_ids)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
