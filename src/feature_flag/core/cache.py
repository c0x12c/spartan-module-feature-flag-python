from typing import Any

import orjson
from asyncpg.pgproto.pgproto import UUID as AsyncpgUUID
from redis import RedisCluster


def orjson_default(obj):
    if isinstance(obj, AsyncpgUUID):
        return str(obj)  # Convert UUID to string
    raise TypeError(f"Type is not JSON serializable: {type(obj)}")


class RedisCache:
    def __init__(self, connection: RedisCluster, namespace: str = ""):
        self.connection = connection
        self.namespace = namespace

    def _format_key(self, key: str):
        return f"{self.namespace}:{key}" if self.namespace else key

    def set(self, key: str, value: Any):
        formatted_key = self._format_key(key)
        serialized_value = orjson.dumps(value, default=orjson_default)  # Use the custom serialization function
        self.connection.set(formatted_key, serialized_value)

    def get(self, key: str):
        formatted_key = self._format_key(key)
        value = self.connection.get(formatted_key)

        if value is None:
            return None

        return orjson.loads(value)

    def delete(self, key: str):
        formatted_key = self._format_key(key)
        self.connection.delete(formatted_key)
