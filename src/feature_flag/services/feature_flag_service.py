import asyncio
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID

from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.core.base_repository import BaseRepository
from feature_flag.core.cache import RedisCache
from feature_flag.core import (
    FeatureFlagNotFoundError,
    FeatureFlagValidationError,
    FeatureFlagCacheError,
    FeatureFlagDatabaseError
)
from feature_flag.repositories.postgres_repository import PostgresRepository

logger = logging.getLogger(__name__)


class FeatureFlagService:
    def __init__(self, repository: PostgresRepository, cache: Optional[RedisCache] = None):
        """
         Initialize the FeatureFlagService.

         Args:
             repository (BaseRepository): The repository for database operations.
             cache (Optional[RedisCache]): The cache for improved performance.
         """
        self.repository = repository
        self.cache = cache

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
            self._validate_flag_data(flag_data)
            feature_flag: FeatureFlag = FeatureFlag(**flag_data)

            entity_id = await self.repository.insert(entity=feature_flag)
            feature_flag = await self.repository.get_by_id(entity_id=str(entity_id), entity_class=FeatureFlag)

            if isinstance(feature_flag.id, UUID):
                feature_flag.id = str(feature_flag.id)

            self._update_cache(feature_flag)
            return feature_flag
        except FeatureFlagValidationError as validation_error:
            logger.error(f"Error details: {str(validation_error)}")
            raise FeatureFlagValidationError(f"Validation failed: {str(validation_error)}") from validation_error
        except Exception as e:
            logger.error(f"Error creating feature flag: {str(e)}")
            raise FeatureFlagDatabaseError(f"Failed to create feature flag: {str(e)}")

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
            if self.cache:
                cached_flag = self.cache.get(key=code)
                if cached_flag:
                    logger.info(f"Feature flag {code} retrieved from cache")
                    return FeatureFlag(**cached_flag) if isinstance(cached_flag, dict) else cached_flag

            flag = await self.repository.get_by_code(code=code, entity_class=FeatureFlag)

            if not flag:
                logger.warning(f"Feature flag with code {code} not found")
                raise FeatureFlagNotFoundError(f"Feature flag with code {code} not found")

            if isinstance(flag.id, UUID):
                flag.id = str(flag.id)

            self._update_cache(flag)
            return flag
        except FeatureFlagNotFoundError as validation_error:
            raise FeatureFlagNotFoundError(f"Feature flag with code {code} not found") from validation_error
        except Exception as e:
            logger.error(f"Error fetching feature flag {code}: {str(e)}")
            raise FeatureFlagDatabaseError(f"Failed to fetch feature flag: {str(e)}")

    async def list_feature_flags(self, limit: int = 100, skip: int = 0) -> List[FeatureFlag]:
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
            flags = await self.repository.list(skip=skip, limit=limit, entity_class=FeatureFlag)
            return flags
        except Exception as e:
            logger.error(f"Error listing feature flags: {str(e)}")
            raise FeatureFlagDatabaseError(f"Failed to list feature flags: {str(e)}")

    async def update_feature_flag(self, code: str, flag_data: Dict[str, Any]) -> FeatureFlag:
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
            self._validate_flag_data(flag_data, update=True)

            existing_flag = await self.repository.get_by_code(code=code, entity_class=FeatureFlag)
            if not existing_flag:
                raise FeatureFlagNotFoundError(f"Feature flag with code {code} not found")

            for key, value in flag_data.items():
                setattr(existing_flag, key, value)

            await self.repository.update(entity=existing_flag)

            self._update_cache(existing_flag)

            return existing_flag
        except FeatureFlagNotFoundError as validation_error:
            logger.error(f"Error updating feature flag: {str(validation_error)}")
            raise FeatureFlagNotFoundError(f"Feature flag update with code {code} not found") from validation_error
        except FeatureFlagValidationError as validation_error:
            logger.error(f"Error updating feature flag: {str(validation_error)}")
            raise FeatureFlagValidationError(str(validation_error)) from validation_error
        except Exception as e:
            logger.error(f"Error updating feature flag {code}: {str(e)}")
            raise FeatureFlagDatabaseError(f"Failed to update feature flag: {str(e)}")

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
            feature_flag = await self.repository.get_by_code(code, entity_class=FeatureFlag)
            if not feature_flag:
                raise FeatureFlagNotFoundError(f"Feature flag with code {code} not found")

            await self.repository.delete(entity_id=feature_flag.id, entity_class=FeatureFlag)

            if self.cache:
                self.cache.delete(key=code)
        except FeatureFlagNotFoundError as validation_error:
            logger.error(f"Error deleting feature flag: {str(validation_error)}")
            raise FeatureFlagNotFoundError(f"Feature flag delete with code {code} not found") from validation_error
        except Exception as e:
            logger.error(f"Error deleting feature flag {code}: {str(e)}")
            raise FeatureFlagDatabaseError(f"Failed to delete feature flag: {str(e)}")

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
        return await self._set_feature_flag_state(code, True)

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
        return await self._set_feature_flag_state(code, False)

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
        try:
            feature_flag = await self.repository.get_by_code(code, entity_class=FeatureFlag)
            if not feature_flag:
                raise FeatureFlagNotFoundError(f"Feature flag with code {code} not found")

            feature_flag.enabled = state
            await self.repository.update(entity=feature_flag)
            self._update_cache(feature_flag)
            return feature_flag
        except FeatureFlagNotFoundError as validation_error:
            logger.error(f"Error updating feature flag: {str(validation_error)}")
            raise FeatureFlagNotFoundError(f"Feature flag with code {code} not found") from validation_error
        except Exception as e:
            logger.error(f"Error {'enabling' if state else 'disabling'} feature flag {code}: {str(e)}")
            raise FeatureFlagDatabaseError(f"Failed to {'enable' if state else 'disable'} feature flag: {str(e)}")

    def _update_cache(self, feature_flag: FeatureFlag) -> None:
        """
        Update the cache with the given feature flag.

        Args:
            feature_flag (FeatureFlag): The feature flag to cache.

        Raises:
            FeatureFlagCacheError: If there's an error in cache operation.
        """
        if self.cache:
            try:
                self.cache.set(key=feature_flag.code, value=feature_flag.__dict__)
            except Exception as e:
                logger.error(f"Error updating cache for feature flag {feature_flag.code}: {str(e)}")
                raise FeatureFlagCacheError(f"Failed to update cache: {str(e)}")

    def _validate_flag_data(self, flag_data: Dict[str, Any], update: bool = False) -> None:
        """
        Validate the input data for a feature flag.

        Args:
            flag_data (Dict[str, Any]): The data to validate.
            update (bool): Whether this is for an update operation.

        Raises:
            FeatureFlagValidationError: If the input data is invalid.
        """
        required_fields = ['name', 'code'] if not update else []
        for field in required_fields:
            if field not in flag_data:
                raise FeatureFlagValidationError(f"Missing required field: {field}")

        if 'name' in flag_data:
            if not isinstance(flag_data['name'], str):
                raise FeatureFlagValidationError("'name' field must be a string")
            if len(flag_data['name']) == 0:
                raise FeatureFlagValidationError("'name' field cannot be empty")

        if 'code' in flag_data:
            if not isinstance(flag_data['code'], str):
                raise FeatureFlagValidationError("'code' field must be a string")
            if len(flag_data['code']) == 0:
                raise FeatureFlagValidationError("'code' field cannot be empty")

        if 'enabled' in flag_data:
            if not isinstance(flag_data['enabled'], bool):
                raise FeatureFlagValidationError("'enabled' field must be a boolean")

        if 'description' in flag_data and not isinstance(flag_data['description'], str):
            raise FeatureFlagValidationError("'description' field must be a string")
