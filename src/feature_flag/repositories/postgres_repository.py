from feature_flag.core.base_repository import BaseRepository
from typing import List


class PostgresRepository(BaseRepository):

    def __init__(self, connection):
        self.connection = connection

    def insert(self, entity) -> str:
        table_name = self._get_table_name(type(entity))
        fields = [
            field
            for field in entity.__dataclass_fields__.keys()
            if not entity.__dataclass_fields__[field].metadata.get("exclude_from_db")
        ]
        values = [getattr(entity, field) for field in fields]

        query = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(fields))}) RETURNING id;"

        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        return cursor.fetchone()[0]

    def update(self, entity) -> None:
        table_name = self._get_table_name(type(entity))
        fields = [
            field
            for field in entity.__dataclass_fields__.keys()
            if field != "id"
            and not entity.__dataclass_fields__[field].metadata.get("exclude_from_db")
        ]
        values = [getattr(entity, field) for field in fields]

        set_clause = ", ".join([f"{field} = %s" for field in fields])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s;"

        cursor = self.connection.cursor()
        cursor.execute(query, values + [entity.id])
        self.connection.commit()

    def delete(self, entity_id: str, entity_class) -> None:
        table_name = self._get_table_name(entity_class)
        query = f"DELETE FROM {table_name} WHERE id = %s;"

        cursor = self.connection.cursor()
        cursor.execute(query, (entity_id,))
        self.connection.commit()

    def get_by_id(self, entity_id: str, entity_class) -> object:
        table_name = self._get_table_name(entity_class)
        fields = [field for field in entity_class.__dataclass_fields__.keys()]
        query = f"SELECT {', '.join(fields)} FROM {table_name} WHERE id = %s;"

        cursor = self.connection.cursor()
        cursor.execute(query, (entity_id,))
        row = cursor.fetchone()
        if row:
            return entity_class(**dict(zip(fields, row)))
        return None

    def list_all(self, entity_class) -> List[object]:
        table_name = self._get_table_name(entity_class)
        fields = [field for field in entity_class.__dataclass_fields__.keys()]
        query = f"SELECT {', '.join(fields)} FROM {table_name};"

        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [entity_class(**dict(zip(fields, row))) for row in rows]
