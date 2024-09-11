from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Type

import inflection

T = TypeVar('T')

# Export T along with BaseRepository
__all__ = ['BaseRepository', 'T']


class BaseRepository(ABC, Generic[T]):

    @abstractmethod
    async def insert(self, entity: T) -> str:
        pass

    @abstractmethod
    async def update(self, entity: T) -> None:
        pass

    @abstractmethod
    async def delete(self, entity_id: str, entity_class: Type[T]) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: str, entity_class: Type[T]) -> T:
        pass

    @abstractmethod
    async def get_by_code(self, code: str, entity_class: Type[T]) -> T:
        pass

    @abstractmethod
    async def list(self, skip: int, limit: int, entity_class: Type[T]) -> List[T]:
        pass

    @staticmethod
    def _get_table_name(entity_class: Type[T]) -> str:
        return getattr(
            entity_class, "_table_name", inflection.underscore(entity_class.__name__)
        )
