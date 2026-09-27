from fastapi import FastAPI
from routers import news, users
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

from utils.exception_handlers import register_exception_handlers

app = FastAPI()
# 注册异常处理器
register_exception_handlers(app)
#请求来源 ———>CORS中间件 解决 前端，后端跨域问题（1.协议 2.域名 3.端口）
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    #请求源
    allow_credentials=True, #允许携带Cookie
    allow_methods=["*"],    #允许所有请求方法
    allow_headers=["*"],    #允许所有请求头
)
@app.get("/")
async def root():
    return {"message": "Hello World"}
#注册路由
app.include_router(news.router)
app.include_router(users.router)
