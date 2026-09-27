from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from starlette import status
from crud import news,news_cache
from config.db_config import get_db
from sqlalchemy.ext.asyncio import  AsyncSession
#创建AIPRouter 实例
#prefix 路由前缀     tags 分组/标签
router = APIRouter(prefix="/api/news", tags=["news"])
# 接口实现流程
# 1. 模块化路由 → API 接口规范文档
# 2. 定义模型类 → 数据库表（数据库设计文档）
# 3. 在 crud 文件夹里面创建文件，封装操作数据库的方法
# 4. 在路由处理函数里面调用 crud 封装好的方法，响应结果
@router.get("/categories")
async def categories(skip: int = 0, limit: int = 100,db: AsyncSession = Depends(get_db)):
    categories = await news_cache.get_categories(db, skip, limit)
    return {
            "code": 200,
            "data": categories,
            "message": "分类获取成功"
            }
@router.get("/list")
async def get_list(
        category_id: int = Query(...,alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10,alias="pageSize",le=100),
        db: AsyncSession = Depends(get_db)):
    offset = (page-1)*page_size
    news_list = await news_cache.get_news_list(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    hasmore = (offset+len(news_list)) < total
    return {
        "code": 200,
        "message": "获取新闻成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasmore": hasmore
        }
    }
@router.get("/detail")
async def get_detail(news_id: int = Query(...,alias="id"),db: AsyncSession = Depends(get_db)):
    #1.查询新闻
    news_detail = await news.get_news_detail(db, news_id)
    if news_detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="该新闻不存在")
        # 实时更新浏览量
    views_res = await news.add_news_view(db, news_id)
    if views_res is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新新闻浏览量失败")
    # 2. 查询同分类相关新闻（排除自己，取3条）
    related_list = await news.get_related_news(
        db=db,
        category_id=news_detail.category_id,
        self_id=news_detail.id,
        limit=5
    )
    # 格式化相关新闻精简字段
    # related_news_data = []
    # for item in related_list:
    #     related_news_data.append({
    #         "id": item.id,
    #         "title": item.title,
    #         "image": item.image,
    #         "publishTime": item.publish_time
    #     })
    return{
        "code": 200,
        "message": "新闻获取成功",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,

            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_list
        }
        }


