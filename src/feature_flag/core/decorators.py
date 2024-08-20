def table_name(name: str):
    def decorator(cls):
        cls._table_name = name
        return cls

    return decorator
