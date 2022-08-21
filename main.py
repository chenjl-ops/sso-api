from fastapi import FastAPI, Query
from fastapi import BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
import uvicorn
from pkg.mysql.database import engine
from sqlalchemy.orm import sessionmaker
from fastapi_utils.tasks import repeat_every

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app_name = "sso-api"
app = FastAPI(
    title="sso-api",
    description="SSO API",
    version="0.1.0",
)

origins = [
    "http://127.0.0.1:8080"
]

# 跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# log 相关配置
log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"

@app.get("/test", summary="测试接口", tags=["Test"])
def test():
    return {"message": "hello test"}

@app.on_event("startup")
@repeat_every(seconds=60)
def test_repeat() -> None:
    print("test repeat success")


# 路由注册相关配置
from internal.users.views import users_router

app.include_router(users_router, prefix="/user")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='FastApi Run Server Args')
    parser.add_argument('--port', type=int)
    args = parser.parse_args()
    port = args.port
    uvicorn.run(app, log_config=log_config, port=port, host="0.0.0.0")

