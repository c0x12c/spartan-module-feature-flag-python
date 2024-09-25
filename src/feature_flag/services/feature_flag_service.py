import logging
from typing import Optional, List, Dict, Any
from uuid import UUID

from feature_flag.core import FeatureFlagNotFoundError, FeatureFlagError
from feature_flag.core.cache import RedisCache
from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.notification.actions import ChangeStatus
from feature_flag.notification.notifier import Notifier
from feature_flag.repositories.postgres_repository import PostgresRepository

logger = logging.getLogger(__name__)


class FeatureFlagService:
    def __init__(
        self,
        repository: PostgresRepository,
        cache: Optional[RedisCache] = None,
        notifier: Optional[Notifier] = None,
    ):
        self.repository = repository
        self.cache = cache
        self.notifier = notifier

    async def create_feature_flag(self, flag_data: Dict[str, Any]) -> FeatureFlag:
        """
        Create a new feature flag.

        Args:
            flag_data (Dict[str, Any]): The data for the new feature flag.

        Returns:
            FeatureFlag: The created feature flag.

        Raises:
            FeatureFlagValidationError: If the input data is invalid.
            FeatureFlagDatabaseError: If there's an error in database operation.
        """
        try:
            logger.info("Creating feature flag with data: %s", flag_data)
            feature_flag = FeatureFlag(**flag_data)
            entity_id = await self.repository.insert(entity=feature_flag)
            feature_flag = await self.repository.get_by_id(
                entity_id=str(entity_id), entity_class=FeatureFlag
            )
            feature_flag.id = (
                str(feature_flag.id)
                if isinstance(feature_flag.id, UUID)
                else feature_flag.id
            )
            self._update_cache(feature_flag)
            logger.info(
                "Feature flag created successfully with ID: %s", feature_flag.id
            )
            return feature_flag
        except Exception as e:
            raise FeatureFlagError(f"Failed to create feature flag: {str(e)}") from e

    async def get_feature_flag_by_code(self, code: str) -> FeatureFlag:
        """
        Get a feature flag by its code.

        Args:
            code (str): The code of the feature flag.

        Returns:
            FeatureFlag: The retrieved feature flag.

        Raises:
            FeatureFlagNotFoundError: If the feature flag is not found.
            FeatureFlagCacheError: If there's an error in cache operation.
            FeatureFlagDatabaseError: If there's an error in database operation.
        """
        try:
            logger.info("Fetching feature flag by code: %s", code)
            flag = await self._fetch_feature_flag_by_code(code=code)
            if not flag:
                raise FeatureFlagNotFoundError(
                    f"Feature flag with code {code} not found"
                )

            flag.id = str(flag.id) if isinstance(flag.id, UUID) else flag.id
            self._update_cache(flag)
            logger.info("Feature flag fetched successfully with code: %s", code)
            return flag
        except FeatureFlagNotFoundError:
            raise
        except Exception as e:
            raise FeatureFlagError(f"Failed to fetch feature flag: {str(e)}") from e

    async def list_feature_flags(
        self, limit: int = 100, skip: int = 0
    ) -> List[FeatureFlag]:
        """
        List feature flags with pagination.

        Args:
            limit (int): The maximum number of flags to return.
            skip (int): The number of flags to skip.

        Returns:
            List[FeatureFlag]: A list of feature flags.

        Raises:
            FeatureFlagDatabaseError: If there's an error in database operation.
        """
        try:
            return await self.repository.list(
                skip=skip, limit=limit, entity_class=FeatureFlag
            )
        except Exception as e:
            raise FeatureFlagError(f"Failed to list feature flags: {str(e)}") from e

    async def update_feature_flag(
        self, code: str, flag_data: Dict[str, Any]
    ) -> FeatureFlag:
        """
        Update an existing feature flag.

        Args:
            code (str): The code of the feature flag to update.
            flag_data (Dict[str, Any]): The updated data for the feature flag.

        Returns:
            FeatureFlag: The updated feature flag.

        Raises:
            FeatureFlagNotFoundError: If the feature flag is not found.
            FeatureFlagValidationError: If the input data is invalid.
            FeatureFlagDatabaseError: If there's an error in database operation.
        """
        try:
            logger.info(
                "Updating feature flag with code: %s and data: %s", code, flag_data
            )
            existing_flag = await self._fetch_feature_flag_by_code(code=code)
            if not existing_flag:
                raise FeatureFlagNotFoundError(
                    f"Feature flag with code {code} not found"
                )

            for key, value in flag_data.items():
                setattr(existing_flag, key, value)

            await self.repository.update(entity=existing_flag)
            self._update_cache(existing_flag)
            if self.notifier:
                self.notifier.send(existing_flag, ChangeStatus.UPDATED)
            logger.info("Feature flag with code %s updated successfully", code)
            return existing_flag
        except FeatureFlagNotFoundError:
            raise
        except Exception as e:
            raise FeatureFlagError(f"Failed to update feature flag: {str(e)}") from e

    async def delete_feature_flag(self, code: str) -> None:
        """
        Delete a feature flag.

        Args:
            code (str): The code of the feature flag to delete.

        Raises:
            FeatureFlagNotFoundError: If the feature flag is not found.
            FeatureFlagDatabaseError: If there's an error in database operation.
        """
        try:
            logger.info("Deleting feature flag with code: %s", code)
            feature_flag = await self._fetch_feature_flag_by_code(code=code)
            if not feature_flag:
                raise FeatureFlagNotFoundError(
                    f"Feature flag with code {code} not found"
                )

            await self.repository.delete(
                entity_id=feature_flag.id, entity_class=FeatureFlag
            )
            if self.cache:
                self.cache.delete(key=code)
            if self.notifier:
                self.notifier.send(feature_flag, ChangeStatus.DELETED)
            logger.info("Feature flag with code %s deleted successfully", code)
        except FeatureFlagNotFoundError:
            raise
        except Exception as e:
            raise FeatureFlagError(f"Failed to delete feature flag: {str(e)}") from e

    async def enable_feature_flag(self, code: str) -> FeatureFlag:
        """
        Enable a feature flag.

        Args:
            code (str): The code of the feature flag to enable.

        Returns:
            FeatureFlag: The updated feature flag.

        Raises:
            FeatureFlagNotFoundError: If the feature flag is not found.
            FeatureFlagDatabaseError: If there's an error in database operation.
        """
        try:
            logger.info("Enabling feature flag with code: %s", code)
            feature_flag = await self._set_feature_flag_state(code, True)
            if self.notifier:
                self.notifier.send(feature_flag, ChangeStatus.ENABLED)
            logger.info("Feature flag with code %s enabled successfully", code)
            return feature_flag
        except FeatureFlagNotFoundError:
            # Exception is re-raised; no need to log the error here
            raise
        except Exception as e:
            raise FeatureFlagError(f"Failed to enable feature flag: {str(e)}") from e

    async def disable_feature_flag(self, code: str) -> FeatureFlag:
        """
        Disable a feature flag.

        Args:
            code (str): The code of the feature flag to disable.

        Returns:
            FeatureFlag: The updated feature flag.

        Raises:
            FeatureFlagNotFoundError: If the feature flag is not found.
            FeatureFlagDatabaseError: If there's an error in database operation.
        """
        try:
            logger.info("Disabling feature flag with code: %s", code)
            feature_flag = await self._set_feature_flag_state(code, False)
            if self.notifier:
                self.notifier.send(feature_flag, ChangeStatus.DISABLED)
            logger.info("Feature flag with code %s disabled successfully", code)
            return feature_flag
        except FeatureFlagNotFoundError:
            raise
        except Exception as e:
            raise FeatureFlagError(f"Failed to disable feature flag: {str(e)}") from e

    async def _set_feature_flag_state(self, code: str, state: bool) -> FeatureFlag:
        """
        Set the state of a feature flag.

        Args:
            code (str): The code of the feature flag.
            state (bool): The new state of the feature flag.

        Returns:
            FeatureFlag: The updated feature flag.

        Raises:
            FeatureFlagNotFoundError: If the feature flag is not found.
            FeatureFlagDatabaseError: If there's an error in database operation.
        """
        feature_flag = await self._fetch_feature_flag_by_code(code=code)
        if not feature_flag:
            raise FeatureFlagNotFoundError(f"Feature flag with code {code} not found")

        feature_flag.enabled = state
        await self.repository.update(entity=feature_flag)
        self._update_cache(feature_flag)
        return feature_flag

    async def _fetch_feature_flag_by_code(self, code: str):
        if self.cache:
            cached_flag = self.cache.get(key=code)
            if cached_flag:
                return (
                    FeatureFlag(**cached_flag)
                    if isinstance(cached_flag, dict)
                    else cached_flag
                )

        return await self.repository.get_by_code(code=code, entity_class=FeatureFlag)

    def _update_cache(self, feature_flag: FeatureFlag) -> None:
        """
        Update the cache with the given feature flag.

        Args:
            feature_flag (FeatureFlag): The feature flag to cache.

        Raises:
            FeatureFlagCacheError: If there's an error in cache operation.
        """
        if self.cache:
            self.cache.set(key=feature_flag.code, value=feature_flag.__dict__)
