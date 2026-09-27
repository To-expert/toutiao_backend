import traceback
import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

# --------------------------配置区--------------------------
# True=开发环境(返回详细报错)  False=生产环境(隐藏敏感信息)
DEBUG_MODE = True
# 日志实例
logger = logging.getLogger("fastapi-exception")
# -----------------------------------------------------------


async def http_exception_handler(request: Request, exc: HTTPException):
    """业务主动抛出的HTTP异常"""
    logger.warning(
        f"【业务异常】url={request.url} status={exc.status_code} detail={exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """数据库完整性约束异常：唯一键冲突、外键异常"""
    error_msg = str(exc.orig)
    logger.error(
        f"【数据库约束异常】url={request.url} error={error_msg}\n{traceback.format_exc()}"
    )

    if "username_UNIQUE" in error_msg or "Duplicate entry" in error_msg:
        detail = "用户名已存在"
    elif "FOREIGN KEY" in error_msg:
        detail = "关联数据不存在"
    else:
        detail = "数据约束冲突，请检查输入"

    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": "IntegrityError",
            "error_detail": error_msg,
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,
            "message": detail,
            "data": error_data
        }
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """通用SQLAlchemy数据库异常"""
    err_stack = traceback.format_exc()
    logger.error(f"【数据库异常】url={request.url} err={str(exc)}\n{err_stack}")

    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,
            "error_detail": str(exc),
            "traceback": err_stack,
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "数据库操作失败，请稍后重试",
            "data": error_data
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """兜底：捕获所有未处理异常"""
    err_stack = traceback.format_exc()
    logger.error(f"【服务器未知异常】url={request.url} err={str(exc)}\n{err_stack}")

    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,
            "error_detail": str(exc),
            "traceback": err_stack,
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": error_data
        }
    )