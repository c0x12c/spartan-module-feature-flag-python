import unittest
import uuid

from faker import Faker
from fastapi.testclient import TestClient

from tests.test_app import app
from tests.test_utils import (
    get_db_connection,
    get_redis_connection,
    setup_database,
    teardown_database,
    random_word,
)

fake = Faker()


class TestFeatureFlagAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db_connection = get_db_connection()
        cls.redis_connection = get_redis_connection()
        setup_database(cls.db_connection)

    @classmethod
    def tearDownClass(cls):
        teardown_database(cls.db_connection)
        cls.db_connection.close()

    def test_create_flag(self):
        flag_data = {
            "name": random_word(),
            "code": random_word(),
            "description": fake.sentence(),
            "enabled": True,
        }
        response = self.client.post("/api/feature-flags", json=flag_data)
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(response_data["name"], flag_data["name"])
        self.assertEqual(response_data["code"], flag_data["code"])
        self.assertEqual(response_data["description"], flag_data["description"])
        self.assertEqual(response_data["enabled"], flag_data["enabled"])

    def test_get_flag(self):
        flag_data = {
            "name": random_word(),
            "code": random_word(),
            "description": fake.sentence(),
            "enabled": True,
        }
        # Insert directly to simulate existing data
        response = self.client.post("/api/feature-flags", json=flag_data)
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        flag_id = response_data["id"]

        response = self.client.get(f"/api/feature-flags/{flag_id}")
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(response_data["id"], flag_id)
        self.assertEqual(response_data["name"], flag_data["name"])
        self.assertEqual(response_data["code"], flag_data["code"])
        self.assertEqual(response_data["description"], flag_data["description"])
        self.assertEqual(response_data["enabled"], flag_data["enabled"])

    def test_enable_flag(self):
        flag_data = {
            "name": random_word(),
            "code": random_word(),
            "description": fake.sentence(),
            "enabled": False,
        }
        response = self.client.post("/api/feature-flags", json=flag_data)
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        flag_id = response_data["id"]

        response = self.client.post(f"/api/feature-flags/{flag_id}/enable")
        self.assertEqual(response.status_code, 200)

    def test_disable_flag(self):
        flag_id = str(uuid.uuid4())
        flag_data = {
            "id": flag_id,
            "name": random_word(),
            "code": random_word(),
            "description": fake.sentence(),
            "enabled": True,
        }
        response = self.client.post("/api/feature-flags", json=flag_data)
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        flag_id = response_data["id"]

        response = self.client.post(f"/api/feature-flags/{flag_id}/disable")
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(response_data["id"], flag_id)
        self.assertEqual(response_data["enabled"], False)


if __name__ == "__main__":
    unittest.main()
