from fastapi import FastAPI, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from redis import RedisCluster
from sqlalchemy.ext.asyncio import AsyncSession

from feature_flag.core.cache import RedisCache
from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.repositories.postgres_repository import PostgresRepository
from feature_flag.services.feature_flag_service import FeatureFlagService
from feature_flag.core import (
    FeatureFlagNotFoundError,
    FeatureFlagValidationError,
    FeatureFlagDatabaseError
)
from tests.test_utils import get_redis_connection, get_db_session

app = FastAPI()


def get_feature_flag_service(
        db_connection: AsyncSession = Depends(get_db_session),
        redis_connection: RedisCluster = Depends(get_redis_connection),
):
    repository = PostgresRepository(db_connection)
    cache = RedisCache(redis_connection, namespace="feature-flag")
    return FeatureFlagService(repository, cache)


@app.post("/api/feature-flags")
async def create_flag(
        flag_data: dict, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    try:
        feature_flag = await service.create_feature_flag(flag_data)
        return jsonable_encoder(feature_flag)
    except FeatureFlagValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FeatureFlagDatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/feature-flags")
async def list_flags(
        skip: int = 0, limit: int = 100, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    try:
        feature_flags = await service.list_feature_flags(limit=limit, skip=skip)
        return jsonable_encoder(feature_flags)
    except FeatureFlagDatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/feature-flags/{code}")
async def get_flag(
        code: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    try:
        feature_flag = await service.get_feature_flag_by_code(code)
        return jsonable_encoder(feature_flag)
    except FeatureFlagNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FeatureFlagDatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/feature-flags/{code}")
async def update_flag(
        code: str,
        flag_data: dict,
        service: FeatureFlagService = Depends(get_feature_flag_service),
):
    try:
        updated_flag = await service.update_feature_flag(code, flag_data)
        return jsonable_encoder(updated_flag)
    except FeatureFlagNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FeatureFlagValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FeatureFlagDatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/feature-flags/{code}")
async def delete_flag(
        code: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    try:
        await service.delete_feature_flag(code)
        return {"message": f"Feature flag with code {code} has been deleted"}
    except FeatureFlagNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FeatureFlagDatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feature-flags/{code}/enable", response_model=FeatureFlag)
async def enable_feature_flag(
        code: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    try:
        flag = await service.enable_feature_flag(code)
        return jsonable_encoder(flag)
    except FeatureFlagNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FeatureFlagDatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feature-flags/{code}/disable", response_model=FeatureFlag)
async def disable_feature_flag(
        code: str, service: FeatureFlagService = Depends(get_feature_flag_service)
):
    try:
        flag = await service.disable_feature_flag(code)
        return jsonable_encoder(flag)
    except FeatureFlagNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FeatureFlagDatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
