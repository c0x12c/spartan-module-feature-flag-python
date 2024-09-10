from dataclasses import replace
from typing import Optional, List
from uuid import UUID

from redis import RedisCluster

from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.core.base_repository import BaseRepository
from feature_flag.core.cache import RedisCache


class FeatureFlagService:
    def __init__(self, repository: BaseRepository, cache: Optional[RedisCache] = None):
        self.repository = repository
        self.cache = cache

    async def create_feature_flag(self, flag_data: dict):
        entity_id = await self.repository.insert(entity=FeatureFlag(**flag_data))
        feature_flag = await self.repository.get_by_id(
            entity_id=str(entity_id), entity_class=FeatureFlag
        )

        if isinstance(feature_flag.id, UUID):
            feature_flag.id = str(feature_flag.id)

        if self.cache:
            self.cache.set(key=feature_flag.code, value=feature_flag)

        return feature_flag

    async def get_feature_flag_by_code(self, code: str) -> Optional[FeatureFlag]:
        if self.cache:
            cached_flag = self.cache.get(key=code)
            if cached_flag:
                return cached_flag

        flag = await self.repository.get_by_code(code=code, entity_class=FeatureFlag)

        if flag and self.cache:
            self.cache.set(key=code, value=flag)

        return flag

    async def list_feature_flags(self, limit: int = 100, skip: int = 0) -> List[FeatureFlag]:
        flags = await self.repository.list_feature_flags(skip=skip, limit=limit, entity_class=FeatureFlag)
        return flags

    async def update_feature_flag(self, code: str, flag_data: dict):
        existing_flag = await self.get_feature_flag_by_code(code)
        if not existing_flag:
            raise ValueError(f"Feature flag with code {code} does not exist.")

        # If existing_flag is a dict, convert it back to FeatureFlag
        if isinstance(existing_flag, dict):
            existing_flag = FeatureFlag(**existing_flag)

        # Remove 'id' from flag_data if it's present to avoid duplication
        flag_data.pop("id", None)

        # Merge the existing flag with the updated fields
        for key, value in flag_data.items():
            setattr(existing_flag, key, value)

        # Update the repository
        await self.repository.update(entity=existing_flag)

        if self.cache:
            self.cache.set(key=existing_flag.code, value=existing_flag)

    async def enable_feature_flag(self, code: str):
        flag_data = {"enabled": True}
        await self.update_feature_flag(code, flag_data)

    async def disable_feature_flag(self, code: str):
        flag_data = {"enabled": False}
        await self.update_feature_flag(code, flag_data)

    async def delete_feature_flag(self, code: str):
        feature_flag = await self.repository.get_by_code(code, entity_class=FeatureFlag)
        await self.repository.delete(entity_id=feature_flag.id)
        if self.cache:
            self.cache.delete(key=feature_flag.code)
