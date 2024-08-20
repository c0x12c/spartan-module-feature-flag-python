from abc import ABC, abstractmethod
from typing import List

import inflection


class BaseRepository(ABC):

    @abstractmethod
    def insert(self, entity) -> str:
        pass

    @abstractmethod
    def update(self, entity) -> None:
        pass

    @abstractmethod
    def delete(self, entity_id: str, entity_class) -> None:
        pass

    @abstractmethod
    def get_by_id(self, entity_id: str, entity_class) -> object:
        pass

    @abstractmethod
    def list_all(self, entity_class) -> List[object]:
        pass

    @staticmethod
    def _get_table_name(entity_class):
        return getattr(
            entity_class, "_table_name", inflection.underscore(entity_class.__name__)
        )
