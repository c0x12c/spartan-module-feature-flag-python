import psycopg2
import redis
from fastapi import FastAPI, HTTPException

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
redis_connection = redis.Redis(host='localhost', port=6379, db=0)
cache = RedisCache(connection=redis_connection, namespace="feature-flag")

# Initialize FeatureFlagService
service = FeatureFlagService(repository=repository, cache=cache)


@app.post("/api/feature-flags", response_model=FeatureFlag)
async def create_feature_flag(flag_data: dict):
    return service.create_feature_flag(flag_data)


@app.get("/api/feature-flags/{flag_id}", response_model=FeatureFlag)
async def get_feature_flag(flag_id: str):
    flag = service.get_feature_flag(flag_id)
    if flag is None:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return flag


@app.patch("/api/feature-flags/{flag_id}/enable", response_model=FeatureFlag)
async def enable_feature_flag(flag_id: str):
    service.enable_feature_flag(flag_id)
    flag = service.get_feature_flag(flag_id)
    return flag


@app.patch("/api/feature-flags/{flag_id}/disable", response_model=FeatureFlag)
async def disable_feature_flag(flag_id: str):
    service.disable_feature_flag(flag_id)
    flag = service.get_feature_flag(flag_id)
    return flag


@app.delete("/api/feature-flags/{flag_id}")
async def delete_feature_flag(flag_id: str):
    service.delete_feature_flag(flag_id)
    return {"status": "deleted"}
