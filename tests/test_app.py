from fastapi import FastAPI, Depends
from fastapi.encoders import jsonable_encoder

from feature_flag.core.cache import RedisCache
from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.repositories.postgres_repository import PostgresRepository
from feature_flag.services.feature_flag_service import FeatureFlagService
from tests.test_utils import get_redis_connection, get_db_connection


def get_feature_flag_service(
    db_connection=Depends(get_db_connection),
    redis_connection=Depends(get_redis_connection),
):
    repository = PostgresRepository(db_connection)
    cache = RedisCache(redis_connection, namespace="feature-flag")
    return FeatureFlagService(repository, cache)


app = FastAPI()


@app.post("/api/feature-flags")
async def create_flag(
    flag_data: dict, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    feature_flag = service.create_feature_flag(flag_data)
    return jsonable_encoder(feature_flag)


@app.get("/api/feature-flags/{id}")
async def get_flag(
    id: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    feature_flag = service.get_feature_flag(id)
    return jsonable_encoder(feature_flag)


@app.put("/api/feature-flags/{id}")
async def update_flag(
    id: str,
    flag_data: dict,
    service: FeatureFlagService = Depends(get_feature_flag_service),
):
    return service.update_feature_flag(id, flag_data)


@app.delete("/api/feature-flags/{id}")
async def delete_flag(
    id: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    return service.delete_feature_flag(id)


@app.post("/api/feature-flags/{flag_id}/enable", response_model=FeatureFlag)
async def enable_feature_flag(
    flag_id: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    service.enable_feature_flag(flag_id)
    flag = service.get_feature_flag(flag_id)
    return flag


@app.post("/api/feature-flags/{flag_id}/disable", response_model=FeatureFlag)
async def disable_feature_flag(
    flag_id: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    service.disable_feature_flag(flag_id)
    flag = service.get_feature_flag(flag_id)
    return flag
