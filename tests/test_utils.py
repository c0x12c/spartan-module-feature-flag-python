import os
import string
from asyncio import current_task
from typing import AsyncGenerator
from unittest.mock import MagicMock

import sqlparse
from faker import Faker
from redis import RedisCluster
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
)

from feature_flag.notification.change_status import ChangeStatus
from feature_flag.notification.slack_notifier import SlackNotifier

fake = Faker()
DATABASE_URL = "postgresql+asyncpg://local:local@localhost:5432/local"

# Initialize the async engine and session factory
engine = create_async_engine(DATABASE_URL, echo=True)
session_factory = async_scoped_session(
    async_sessionmaker(
        engine,
        expire_on_commit=False,
    ),
    scopefunc=current_task,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.

    :yield: database session.
    """
    session: AsyncSession = session_factory()

    try:  # noqa: WPS501
        yield session

    finally:
        await session.commit()
        await session.close()


def get_redis_connection():
    # Initialize the RedisCluster object
    return RedisCluster.from_url(url=f"redis://localhost:30001", decode_responses=True)


mock_slack_notifier = MagicMock(
    wraps=SlackNotifier(
        slack_webhook_url="xxx", excluded_statuses=[ChangeStatus.ENABLED]
    )
)


def get_slack_notifier():
    global mock_slack_notifier
    mock_slack_notifier.send = MagicMock(name="send")
    return mock_slack_notifier


async def setup_database(session: AsyncSession, sql_file="setup.sql"):
    # Get the absolute path to the SQL file
    sql_file_path = os.path.join(os.path.dirname(__file__), sql_file)

    # Read the SQL file
    with open(sql_file_path, "r") as f:
        sql_commands = f.read()

    # Use sqlparse to safely split the SQL file into individual statements
    sql_statements = sqlparse.split(sql_commands)

    # Execute each SQL statement separately using the async session
    async with session.begin():
        for statement in sql_statements:
            statement = statement.strip()
            if statement:
                await session.execute(text(statement))


async def teardown_database(session: AsyncSession):
    # SQL command to drop the table
    drop_table_sql = "DROP TABLE IF EXISTS feature_flags;"
    drop_routine_sql = "DROP ROUTINE IF EXISTS update_updated_at();"

    # Execute the SQL command using the async session
    async with session.begin():
        await session.execute(text(drop_table_sql))
        await session.execute(text(drop_routine_sql))


def random_word(length=10):
    return "".join(fake.random_choices(elements=string.ascii_lowercase, length=length))
