from abc import ABC, abstractmethod
from typing import List

import inflection


class BaseRepository(ABC):

    @abstractmethod
    async def insert(self, entity) -> str:
        pass

    @abstractmethod
    async def update(self, entity) -> None:
        pass

    @abstractmethod
    async def delete(self, entity_id: str, entity_class) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: str, entity_class) -> object:
        pass

    @abstractmethod
    async def get_by_code(self, code: str, entity_class) -> object:
        pass

    @abstractmethod
    async def list_feature_flags(self, skip: int, limit: int, entity_class) -> List[object]:
        pass

    @staticmethod
    def _get_table_name(entity_class):
        return getattr(
            entity_class, "_table_name", inflection.underscore(entity_class.__name__)
        )
