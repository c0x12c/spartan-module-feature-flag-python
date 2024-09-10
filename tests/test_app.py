from fastapi import FastAPI, Depends
from fastapi.encoders import jsonable_encoder
from redis import RedisCluster
from sqlalchemy.ext.asyncio import AsyncSession

from feature_flag.core.cache import RedisCache
from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.repositories.postgres_repository import PostgresRepository
from feature_flag.services.feature_flag_service import FeatureFlagService
from tests.test_utils import get_redis_connection, get_db_session


def get_feature_flag_service(
    db_connection: AsyncSession = Depends(get_db_session),
    redis_connection: RedisCluster = Depends(get_redis_connection),
):
    repository = PostgresRepository(db_connection)
    cache = RedisCache(redis_connection, namespace="feature-flag")
    return FeatureFlagService(repository, cache)


app = FastAPI()


@app.post("/api/feature-flags")
async def create_flag(
    flag_data: dict, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    feature_flag = await service.create_feature_flag(flag_data)
    return jsonable_encoder(feature_flag)

@app.get("/api/feature-flags/list")
async def get_flag(
    skip: int, limit: int, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    feature_flags = await service.list_feature_flags(limit=limit, skip=skip)
    return jsonable_encoder(feature_flags)

@app.get("/api/feature-flags/{code}")
async def get_flag(
    code: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    feature_flag = await service.get_feature_flag_by_code(code)
    return jsonable_encoder(feature_flag)


@app.put("/api/feature-flags/{code}")
async def update_flag(
    code: str,
    flag_data: dict,
    service: FeatureFlagService = Depends(get_feature_flag_service),
):
    return await service.update_feature_flag(code, flag_data)


@app.delete("/api/feature-flags/{code}")
async def delete_flag(
    code: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    return await service.delete_feature_flag(code)


@app.post("/api/feature-flags/{code}/enable", response_model=FeatureFlag)
async def enable_feature_flag(
    code: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    await service.enable_feature_flag(code)
    flag = await service.get_feature_flag_by_code(code)
    return flag


@app.post("/api/feature-flags/{code}/disable", response_model=FeatureFlag)
async def disable_feature_flag(
    code: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    await service.disable_feature_flag(code)
    flag = await service.get_feature_flag_by_code(code)
    return flag
