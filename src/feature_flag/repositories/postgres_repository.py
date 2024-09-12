from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Type

from feature_flag.core.base_repository import BaseRepository, T


class PostgresRepository(BaseRepository[T]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, entity: T) -> str:
        table_name = self._get_table_name(type(entity))
        fields = [
            field
            for field in entity.__dataclass_fields__.keys()
            if not entity.__dataclass_fields__[field].metadata.get("exclude_from_db")
        ]
        values = [getattr(entity, field) for field in fields]

        query = (f"INSERT INTO {table_name} ({', '.join(fields)})"
                 f" VALUES ({', '.join([f':{field}' for field in fields])}) RETURNING id;")

        result = await self.session.execute(text(query), dict(zip(fields, values)))
        return result.scalar()

    async def update(self, entity: T) -> None:
        table_name = self._get_table_name(type(entity))
        fields = [
            field
            for field in entity.__dataclass_fields__.keys()
            if field != "id" and not entity.__dataclass_fields__[field].metadata.get("exclude_from_db")
        ]
        values = [getattr(entity, field) for field in fields]

        set_clause = ", ".join([f"{field} = :{field}" for field in fields])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = :id;"

        await self.session.execute(
            text(query),
            {**dict(zip(fields, values)), "id": entity.id}
        )

    async def delete(self, entity_id: str, entity_class: Type[T]) -> None:
        table_name = self._get_table_name(entity_class)
        query = f"DELETE FROM {table_name} WHERE id = :id;"

        await self.session.execute(text(query), {"id": entity_id})

    async def get_by_id(self, entity_id: str, entity_class: Type[T]) -> T:
        table_name = self._get_table_name(entity_class)
        fields = [field for field in entity_class.__dataclass_fields__.keys()]
        query = f"SELECT {', '.join(fields)} FROM {table_name} WHERE id = :id;"

        result = await self.session.execute(text(query), {"id": entity_id})
        row = result.fetchone()
        if row:
            return entity_class(**dict(zip(fields, row)))
        return None

    async def get_by_code(self, code: str, entity_class: Type[T]) -> T:
        table_name = self._get_table_name(entity_class)
        fields = [field for field in entity_class.__dataclass_fields__.keys()]
        query = f"SELECT {', '.join(fields)} FROM {table_name} WHERE code = :code;"

        result = await self.session.execute(text(query), {"code": code})
        row = result.fetchone()
        if row:
            return entity_class(**dict(zip(fields, row)))
        return None

    async def list_all(self, entity_class: Type[T]) -> List[T]:
        table_name = self._get_table_name(entity_class)
        fields = [field for field in entity_class.__dataclass_fields__.keys()]
        query = f"SELECT {', '.join(fields)} FROM {table_name};"

        result = await self.session.execute(text(query))
        rows = result.fetchall()
        return [entity_class(**dict(zip(fields, row))) for row in rows]

    async def list(self, skip: int, limit: int, entity_class: Type[T]) -> List[T]:
        table_name = self._get_table_name(entity_class)
        fields = [field for field in entity_class.__dataclass_fields__.keys()]
        query = f"SELECT {', '.join(fields)} FROM {table_name} LIMIT {limit} OFFSET {skip};"

        result = await self.session.execute(text(query))
        rows = result.fetchall()
        return [entity_class(**dict(zip(fields, row))) for row in rows]