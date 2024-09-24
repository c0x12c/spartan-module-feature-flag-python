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
        self.mock_cache.get.return_value = existing_flag

        await self.service.disable_feature_flag(code=existing_flag.code)

        self.mock_repository.get_by_code.assert_not_called()

        expected_flag = FeatureFlag(
            id=flag_id, name=existing_flag.name, code=existing_flag.code, enabled=False
        )

        self.mock_repository.update.assert_called_once_with(entity=expected_flag)
        self.mock_cache.set.assert_called_once()

        call_args = self.mock_cache.set.call_args
        self.assertEqual(call_args[1]["key"], existing_flag.code)
        self.assertEqual(call_args[1]["value"]["name"], existing_flag.name)
        self.assertEqual(call_args[1]["value"]["code"], existing_flag.code)
        self.assertEqual(call_args[1]["value"]["id"], existing_flag.id)
        self.assertFalse(call_args[1]["value"]["enabled"])

    async def test_enable_feature_flag(self):
        flag_id = str(uuid.uuid4())
        existing_flag = FeatureFlag(
            id=flag_id, name=random_word(), code=random_word(), enabled=False
        )
        self.mock_cache.get.return_value = existing_flag

        await self.service.enable_feature_flag(code=existing_flag.code)

        self.mock_repository.get_by_code.assert_not_called()

        expected_flag = FeatureFlag(
            id=flag_id, name=existing_flag.name, code=existing_flag.code, enabled=True
        )
        self.mock_repository.update.assert_called_once_with(entity=expected_flag)
        self.mock_cache.set.assert_called_once()
        call_args = self.mock_cache.set.call_args
        self.assertEqual(call_args[1]["key"], existing_flag.code)
        self.assertEqual(call_args[1]["value"]["name"], existing_flag.name)
        self.assertEqual(call_args[1]["value"]["code"], existing_flag.code)
        self.assertEqual(call_args[1]["value"]["id"], existing_flag.id)
        self.assertTrue(call_args[1]["value"]["enabled"])

    async def test_get_feature_flag(self):
        flag_data = FeatureFlag(
            id=str(uuid.uuid4()), name=random_word(), code=random_word(), enabled=True
        )
        self.mock_cache.get.return_value = flag_data

        result = await self.service.get_feature_flag_by_code(code=flag_data.code)

        self.mock_repository.get_by_code.assert_not_called()

        self.assertEqual(result, flag_data)
        self.mock_cache.get.assert_called_once_with(key=flag_data.code)
        self.mock_repository.get_by_code.assert_not_called()

    async def test_list_feature_flags(self):
        limit = 10
        skip = 2
        await self.service.list_feature_flags(limit=limit, skip=skip)
        self.mock_repository.list.assert_called_once_with(
            limit=limit, skip=skip, entity_class=FeatureFlag
        )

    async def test_update_feature_flag(self):
        existing_flag = FeatureFlag(
            id=str(uuid.uuid4()), name=random_word(), code=random_word(), enabled=True
        )
        self.mock_cache.get.return_value = existing_flag
        flag_data = {
            "name": random_word(),
            "code": existing_flag.code,
            "enabled": False,
        }

        await self.service.update_feature_flag(
            code=flag_data["code"], flag_data=flag_data
        )

        self.mock_repository.get_by_code.assert_not_called()

        self.mock_repository.update.assert_called_once()
        self.mock_cache.set.assert_called_once()

    async def test_delete_feature_flag(self):
        existing_flag = FeatureFlag(
            id=str(uuid.uuid4()), name=random_word(), code=random_word()
        )
        self.mock_cache.get.return_value = existing_flag

        await self.service.delete_feature_flag(code=existing_flag.code)

        self.mock_repository.get_by_code.assert_not_called()

        self.mock_repository.delete.assert_called_once_with(
            entity_id=existing_flag.id, entity_class=FeatureFlag
        )
        self.mock_cache.delete.assert_called_once_with(key=existing_flag.code)


if __name__ == "__main__":
    unittest.main()
