import orjson


class RedisCache:
    def __init__(self, connection, namespace=""):
        self.connection = connection
        self.namespace = namespace

    def _format_key(self, key):
        return f"{self.namespace}:{key}" if self.namespace else key

    def set(self, key, value):
        formatted_key = self._format_key(key)
        self.connection.set(formatted_key, orjson.dumps(value))

    def get(self, key):
        formatted_key = self._format_key(key)
        value = self.connection.get(formatted_key)

        if value is None:
            return None

        return orjson.loads(value)

    def delete(self, key):
        formatted_key = self._format_key(key)
        self.connection.delete(formatted_key)
