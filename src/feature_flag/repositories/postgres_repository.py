from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List

from feature_flag.core.base_repository import BaseRepository


class PostgresRepository(BaseRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert(self, entity) -> str:
        table_name = self._get_table_name(type(entity))
        # Collecting fields that are not excluded from the DB
        fields = [
            field
            for field in entity.__dataclass_fields__.keys()
            if not entity.__dataclass_fields__[field].metadata.get("exclude_from_db")
        ]
        # Extracting values from the entity for each field
        values = [getattr(entity, field) for field in fields]

        # Constructing the query
        query = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join([f':{field}' for field in fields])}) RETURNING id;"

        # Executing the query
        result = await self.session.execute(text(query), dict(zip(fields, values)))
        # Committing the transaction
        await self.session.commit()

        # Returning the id of the newly inserted row
        return result.scalar()

    async def update(self, entity) -> None:
        table_name = self._get_table_name(type(entity))
        fields = [
            field
            for field in entity.__dataclass_fields__.keys()
            if field != "id"
            and not entity.__dataclass_fields__[field].metadata.get("exclude_from_db")
        ]
        values = [getattr(entity, field) for field in fields]

        set_clause = ", ".join([f"{field} = :{field}" for field in fields])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = :id;"

        await self.session.execute(
            text(query),
            {**dict(zip(fields, values)), "id": entity.id}
        )
        await self.session.commit()

    async def delete(self, entity_id: str, entity_class) -> None:
        table_name = self._get_table_name(entity_class)
        query = f"DELETE FROM {table_name} WHERE id = :id;"

        await self.session.execute(text(query), {"id": entity_id})
        await self.session.commit()

    async def get_by_id(self, entity_id: str, entity_class) -> object:
        table_name = self._get_table_name(entity_class)
        fields = [field for field in entity_class.__dataclass_fields__.keys()]
        query = f"SELECT {', '.join(fields)} FROM {table_name} WHERE id = :id;"

        result = await self.session.execute(text(query), {"id": entity_id})
        row = result.fetchone()
        if row:
            return entity_class(**dict(zip(fields, row)))
        return None

    async def list_all(self, entity_class) -> List[object]:
        table_name = self._get_table_name(entity_class)
        fields = [field for field in entity_class.__dataclass_fields__.keys()]
        query = f"SELECT {', '.join(fields)} FROM {table_name};"

        result = await self.session.execute(text(query))
        rows = result.fetchall()
        return [entity_class(**dict(zip(fields, row))) for row in rows]
