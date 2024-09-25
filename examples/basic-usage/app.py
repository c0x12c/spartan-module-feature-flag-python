import os

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from redis import RedisCluster

from feature_flag.core.cache import RedisCache
from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.notification.slack_notifier import SlackNotifier
from feature_flag.repositories.postgres_repository import PostgresRepository
from feature_flag.services.feature_flag_service import FeatureFlagService

# Initialize FastAPI
app = FastAPI()

# Database connection setup
DATABASE_URL = "postgresql+asyncpg://local:local@localhost:5432/local"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Redis connection setup
redis_connection = RedisCluster.from_url(url="redis://localhost:30001", decode_responses=True)
cache = RedisCache(connection=redis_connection, namespace="feature-flag")


# Dependency to get FeatureFlagService
async def get_feature_flag_service(db: AsyncSession = Depends(get_db)):
    repository = PostgresRepository[FeatureFlag](session=db)
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    notifier = SlackNotifier(slack_webhook_url=slack_webhook_url) if slack_webhook_url else None
    return FeatureFlagService(repository=repository, cache=cache, notifier=notifier)


@app.post("/api/feature-flags", response_model=FeatureFlag)
async def create_feature_flag(flag_data: dict, service: FeatureFlagService = Depends(get_feature_flag_service)):
    return await service.create_feature_flag(flag_data)


@app.get("/api/feature-flags/{code}", response_model=FeatureFlag)
async def get_feature(code: str, service: FeatureFlagService = Depends(get_feature_flag_service)):
    flag = await service.get_feature_flag_by_code(code)
    if flag is None:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return flag


@app.patch("/api/feature-flags/{code}/enable", response_model=FeatureFlag)
async def enable_feature_flag(code: str, service: FeatureFlagService = Depends(get_feature_flag_service)):
    flag = await service.enable_feature_flag(code)
    return flag


@app.patch("/api/feature-flags/{code}/disable", response_model=FeatureFlag)
async def disable_feature_flag(code: str, service: FeatureFlagService = Depends(get_feature_flag_service)):
    await service.disable_feature_flag(code)
    flag = await service.get_feature_flag_by_code(code)
    return flag


@app.delete("/api/feature-flags/{code}")
async def delete_feature_flag(code: str, service: FeatureFlagService = Depends(get_feature_flag_service)):
    await service.delete_feature_flag(code)
    return {"status": "deleted"}
