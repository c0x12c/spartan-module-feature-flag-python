from typing import Optional

from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.core.base_repository import BaseRepository
from feature_flag.core.cache import RedisCache


class FeatureFlagService:
    def __init__(self, repository: BaseRepository, cache: Optional[RedisCache] = None):
        self.repository = repository
        self.cache = cache

    def create_feature_flag(self, flag_data: dict):
        entity_id = self.repository.insert(entity=FeatureFlag(**flag_data))
        feature_flag = self.repository.get_by_id(
            entity_id=entity_id, entity_class=FeatureFlag
        )

        if self.cache:
            self.cache.set(key=feature_flag.id, value=feature_flag)

        return feature_flag

    def get_feature_flag(self, entity_id: str) -> Optional[FeatureFlag]:
        if self.cache:
            cached_flag = self.cache.get(key=entity_id)
            if cached_flag:
                return cached_flag

        flag = self.repository.get_by_id(entity_id=entity_id, entity_class=FeatureFlag)

        if flag and self.cache:
            self.cache.set(key=entity_id, value=flag)

        return flag

    def update_feature_flag(self, entity_id: str, flag_data: dict):
        existing_flag = self.get_feature_flag(entity_id)
        if not existing_flag:
            raise ValueError(f"Feature flag with ID {entity_id} does not exist.")

        # If existing_flag is a dict, convert it back to FeatureFlag
        if isinstance(existing_flag, dict):
            existing_flag = FeatureFlag(**existing_flag)

        # Remove 'id' from flag_data if it's present to avoid duplication
        flag_data.pop("id", None)

        # Merge the existing flag with the updated fields
        for key, value in flag_data.items():
            setattr(existing_flag, key, value)

        # Update the repository
        self.repository.update(entity=existing_flag)

        if self.cache:
            self.cache.set(key=existing_flag.id, value=existing_flag)

    def enable_feature_flag(self, entity_id: str):
        flag_data = {"enabled": True}
        self.update_feature_flag(entity_id, flag_data)

    def disable_feature_flag(self, entity_id: str):
        flag_data = {"enabled": False}
        self.update_feature_flag(entity_id, flag_data)

    def delete_feature_flag(self, entity_id: str):
        self.repository.delete(entity_id=entity_id)
        if self.cache:
            self.cache.delete(key=entity_id)
