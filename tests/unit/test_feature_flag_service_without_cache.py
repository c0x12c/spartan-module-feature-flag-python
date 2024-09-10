import unittest
import uuid
from unittest.mock import MagicMock, AsyncMock

from faker import Faker

from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.services.feature_flag_service import FeatureFlagService
from tests.test_utils import random_word

fake = Faker()


class TestFeatureFlagServiceWithoutCache(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_repository = AsyncMock()
        self.service = FeatureFlagService(self.mock_repository, None)

    async def test_disable_feature_flag(self):
        flag_id = str(uuid.uuid4())
        existing_flag = FeatureFlag(
            id=flag_id, name=random_word(), code=random_word(), enabled=True
        )
        self.mock_repository.get_by_id.return_value = existing_flag

        await self.service.disable_feature_flag(flag_id)

        expected_flag = FeatureFlag(
            id=flag_id, name=existing_flag.name, code=existing_flag.code, enabled=False
        )
        self.mock_repository.update.assert_called_once_with(entity=expected_flag)

    async def test_enable_feature_flag(self):
        flag_id = str(uuid.uuid4())
        existing_flag = FeatureFlag(
            id=flag_id, name=random_word(), code=random_word(), enabled=False
        )
        self.mock_repository.get_by_id.return_value = existing_flag

        await self.service.enable_feature_flag(flag_id)

        expected_flag = FeatureFlag(
            id=flag_id, name=existing_flag.name, code=existing_flag.code, enabled=True
        )
        self.mock_repository.update.assert_called_once_with(entity=expected_flag)

    async def test_create_feature_flag(self):
        flag_data = {"name": random_word(), "code": random_word()}
        await self.service.create_feature_flag(flag_data)
        self.mock_repository.insert.assert_called_once()

    async def test_get_feature_flag(self):
        flag_data = FeatureFlag(
            id=str(uuid.uuid4()), name=random_word(), code=random_word()
        )
        self.mock_repository.get_by_id.return_value = flag_data
        result = await self.service.get_feature_flag(flag_data.id)
        self.assertEqual(result, flag_data)

    async def test_update_feature_flag(self):
        flag_data = {"name": random_word(), "code": random_word()}
        await self.service.update_feature_flag(str(uuid.uuid4()), flag_data)
        self.mock_repository.update.assert_called_once()

    async def test_delete_feature_flag(self):
        flag_id = str(uuid.uuid4())
        await self.service.delete_feature_flag(flag_id)
        self.mock_repository.delete.assert_called_once_with(entity_id=flag_id)


if __name__ == "__main__":
    unittest.main()
