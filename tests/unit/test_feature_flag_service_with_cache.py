import unittest
import uuid
from unittest.mock import MagicMock, call, AsyncMock

from faker import Faker

from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.services.feature_flag_service import FeatureFlagService
from tests.test_utils import random_word

fake = Faker()


class TestFeatureFlagServiceWithCache(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_repository = AsyncMock()
        self.mock_cache = MagicMock()
        self.service = FeatureFlagService(self.mock_repository, self.mock_cache)


    async def test_disable_feature_flag(self):
        flag_id = str(uuid.uuid4())
        existing_flag = FeatureFlag(
            id=flag_id, name=random_word(), code=random_word(), enabled=True
        )
        self.mock_cache.get.return_value = None  # Mock cache get method
        self.mock_repository.get_by_code.return_value = existing_flag

        await self.service.disable_feature_flag(code=existing_flag.code)

        expected_flag = FeatureFlag(
            id=flag_id, name=existing_flag.name, code=existing_flag.code, enabled=False
        )
        self.mock_repository.update.assert_called_once_with(entity=expected_flag)
        self.mock_cache.set.assert_has_calls([call(key=existing_flag.code, value=existing_flag)])
        self.mock_cache.set.assert_has_calls([call(key=existing_flag.code, value=expected_flag)])
        # self.mock_cache.set.assert_called_once_with(key=flag_id, value=expected_flag)
        self.mock_cache.get.assert_called_once_with(
            key=existing_flag.code
        )  # Check if cache was hit

    async def test_enable_feature_flag(self):
        flag_id = str(uuid.uuid4())
        existing_flag = FeatureFlag(
            id=flag_id, name=random_word(), code=random_word(), enabled=False
        )
        self.mock_cache.get.return_value = None  # Mock cache get method
        self.mock_repository.get_by_code.return_value = existing_flag

        await self.service.enable_feature_flag(code=existing_flag.code)

        expected_flag = FeatureFlag(
            id=flag_id, name=existing_flag.name, code=existing_flag.code, enabled=True
        )
        self.mock_repository.update.assert_called_once_with(entity=expected_flag)
        self.mock_cache.set.assert_has_calls([call(key=existing_flag.code, value=expected_flag)])
        self.mock_cache.get.assert_called_once_with(
            key=existing_flag.code
        )  # Check if cache was hit

    async def test_create_feature_flag(self):
        flag_data = {"name": random_word(), "code": random_word()}
        await self.service.create_feature_flag(flag_data)
        self.mock_repository.insert.assert_called_once()
        self.mock_cache.set.assert_called_once()

    async def test_get_feature_flag(self):
        flag_data = FeatureFlag(
            id=str(uuid.uuid4()), name=random_word(), code=random_word(), enabled=True
        )
        self.mock_cache.get.return_value = flag_data.__dict__
        result = await self.service.get_feature_flag_by_code(code=flag_data.code)
        self.assertEqual(result, flag_data)
        self.mock_cache.get.assert_called_once_with(key=flag_data.code)
        self.mock_repository.get_by_code.assert_not_called()

    async def test_list_feature_flags(self):
        limit = 10
        skip = 2
        await self.service.list_feature_flags(limit=limit, skip=skip)
        self.mock_repository.list.assert_called_once_with(limit=limit, skip=skip, entity_class=FeatureFlag)

    async def test_update_feature_flag(self):
        flag_data = FeatureFlag(
            id=str(uuid.uuid4()), name=random_word(), code=random_word(), enabled=True
        )
        self.mock_cache.get.return_value = flag_data.__dict__
        flag_data = {"name": random_word(), "code": flag_data.code, 'enabled': False}
        await self.service.update_feature_flag(code=flag_data['code'], flag_data=flag_data)
        self.mock_repository.update.assert_called_once()
        self.mock_cache.set.assert_called_once()

    async def test_delete_feature_flag(self):
        exists_flag = FeatureFlag(id=str(uuid.uuid4()), code=random_word(), name=random_word())
        self.mock_repository.get_by_code.return_value = exists_flag
        await self.service.delete_feature_flag(code=exists_flag.code)
        self.mock_repository.delete.assert_called_once_with(entity_id=exists_flag.id, entity_class=FeatureFlag)
        self.mock_cache.delete.assert_called_once_with(key=exists_flag.code)


if __name__ == "__main__":
    unittest.main()
