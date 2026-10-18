import os

import redis
from fastapi import FastAPI, HTTPException

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

app = FastAPI()
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.post("/hit/{key}")
def hit(key: str):
    try:
        count = r.incr(f"hits:{key}")   # atomic
    except redis.RedisError:
        raise HTTPException(status_code=503, detail="redis unavailable")
    return {"key": key, "count": int(count)}


@app.get("/count/{key}")
def count(key: str):
    try:
        value = r.get(f"hits:{key}")
    except redis.RedisError:
        raise HTTPException(status_code=503, detail="redis unavailable")
    return {"key": key, "count": int(value) if value is not None else 0}


@app.get("/healthz")
def healthz():
    try:
        r.ping()
    except redis.RedisError:
        raise HTTPException(status_code=503, detail={"status": "degraded", "redis": "down"})
    return {"status": "ok", "redis": "up"}
