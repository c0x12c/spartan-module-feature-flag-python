import psycopg2
from fastapi import FastAPI, HTTPException
from redis import RedisCluster

from feature_flag.core.cache import RedisCache
from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.repositories.postgres_repository import PostgresRepository
from feature_flag.services.feature_flag_service import FeatureFlagService

# Initialize FastAPI
app = FastAPI()

# Database connection setup
db_connection = psycopg2.connect(
    dbname="local",
    user="local",
    password="local",
    host="localhost",
    port="5432"
)
repository = PostgresRepository[FeatureFlag](connection=db_connection)

# Redis connection setup
redis_connection = RedisCluster.from_url(url=f"redis://localhost:30001", decode_responses=True)
cache = RedisCache(connection=redis_connection, namespace="feature-flag")

# Initialize FeatureFlagService
service = FeatureFlagService(repository=repository, cache=cache)


@app.post("/api/feature-flags", response_model=FeatureFlag)
async def create_feature_flag(flag_data: dict):
    return await service.create_feature_flag(flag_data)


@app.get("/api/feature-flags/{code}", response_model=FeatureFlag)
async def get_feature(code: str):
    flag = await service.get_feature_flag_by_code(code)
    if flag is None:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return flag


@app.patch("/api/feature-flags/{flag_id}/enable", response_model=FeatureFlag)
async def enable_feature_flag(code: str):
    await service.enable_feature_flag(code)
    flag = service.get_feature_flag_by_code(code)
    return flag


@app.patch("/api/feature-flags/{flag_id}/disable", response_model=FeatureFlag)
async def disable_feature_flag(code: str):
    await service.disable_feature_flag(code)
    flag = service.get_feature_flag_by_code(code)
    return flag


@app.delete("/api/feature-flags/{flag_id}")
async def delete_feature_flag(code: str):
    await service.delete_feature_flag(code)
    return {"status": "deleted"}
