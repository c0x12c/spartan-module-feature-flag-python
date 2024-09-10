import asyncio
import unittest
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_app import app
from tests.test_utils import (
    get_redis_connection,
    setup_database,
    teardown_database,
    random_word,
    session_factory,
)

fake = Faker()

class TestFeatureFlagAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Check if redis_connection is not already set
        cls.redis_connection = get_redis_connection()
        # Initialize event loop and session at the class level
        cls.loop = asyncio.get_event_loop()
        cls.loop.run_until_complete(cls.setUpDatabase())

    @classmethod
    async def setUpDatabase(cls):
        async with cls._get_async_session() as session:
            cls.session = session
            await setup_database(session=session)


    @classmethod
    def tearDownClass(cls):
        cls.loop.run_until_complete(teardown_database(cls.session))

    def test_create_flag(self):
        self.loop.run_until_complete(self.async_test_create_flag())

    async def async_test_create_flag(self):
        flag_data = {
            "name": random_word(),
            "code": random_word(),
            "description": fake.sentence(),
            "enabled": True,
        }
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/feature-flags", json=flag_data)
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertEqual(response_data["name"], flag_data["name"])
            self.assertEqual(response_data["code"], flag_data["code"])
            self.assertEqual(response_data["description"], flag_data["description"])
            self.assertEqual(response_data["enabled"], flag_data["enabled"])

    def test_get_flag(self):
        self.loop.run_until_complete(self.async_test_get_flag())

    async def async_test_get_flag(self):
        flag_data = {
            "name": random_word(),
            "code": random_word(),
            "description": fake.sentence(),
            "enabled": True,
        }
        # Insert directly to simulate existing data
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/feature-flags", json=flag_data)
            self.assertEqual(response.status_code, 200)

            response_data = response.json()
            flag_id = response_data["id"]

            response = await client.get(f"/api/feature-flags/{flag_id}")
            self.assertEqual(response.status_code, 200)

            response_data = response.json()
            self.assertEqual(response_data["id"], flag_id)
            self.assertEqual(response_data["name"], flag_data["name"])
            self.assertEqual(response_data["code"], flag_data["code"])
            self.assertEqual(response_data["description"], flag_data["description"])
            self.assertEqual(response_data["enabled"], flag_data["enabled"])

    def test_enable_flag(self):
        self.loop.run_until_complete(self.async_test_enable_flag())

    async def async_test_enable_flag(self):
        flag_data = {
            "name": random_word(),
            "code": random_word(),
            "description": fake.sentence(),
            "enabled": False,
        }
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/feature-flags", json=flag_data)
            self.assertEqual(response.status_code, 200)

            response_data = response.json()
            flag_id = response_data["id"]

            response = await client.post(f"/api/feature-flags/{flag_id}/enable")
            self.assertEqual(response.status_code, 200)

    def test_disable_flag(self):
        self.loop.run_until_complete(self.async_test_disable_flag())

    async def async_test_disable_flag(self):
        flag_id = str(uuid.uuid4())
        flag_data = {
            "id": flag_id,
            "name": random_word(),
            "code": random_word(),
            "description": fake.sentence(),
            "enabled": True,
        }
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/feature-flags", json=flag_data)
            self.assertEqual(response.status_code, 200)

            response_data = response.json()
            flag_id = response_data["id"]

            response = await client.post(f"/api/feature-flags/{flag_id}/disable")
            self.assertEqual(response.status_code, 200)

            response_data = response.json()
            self.assertEqual(response_data["id"], flag_id)
            self.assertEqual(response_data["enabled"], False)

    @classmethod
    @asynccontextmanager
    async def _get_async_session(cls):
        # Create and manage the session, yield it for usage, and clean up after
        session: AsyncSession = session_factory()  # Ensure this creates an asynchronous session
        try:
            yield session
        finally:
            await session.close()  # Close the session after usage


if __name__ == "__main__":
    unittest.main()
