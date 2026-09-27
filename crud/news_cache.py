from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import get_cached_categories, set_cached_categories, get_cached_list, set_cached_list
from models.news import Category, News

#将新闻分类
async def get_categories(db: AsyncSession,skip: int = 0,limit: int = 100):
    #读取数据
    cache_categories = await get_cached_categories()
    if cache_categories:
        return cache_categories
    rule = select(Category).offset(skip).limit(limit)
    result = await db.execute(rule)
    categories = result.scalars().all()
    #写入数据
    if categories:
        categories = jsonable_encoder(categories)
        await set_cached_categories(categories)
    #返回数据
    return categories
async def get_news_list(db: AsyncSession,category_id: int,skip: int = 0,limit: int = 10):
    #查询指定分类下的所有新闻
    #先尝试从缓存获取新闻列表
    #跳过的数量skip=(页码-1)*每页数量 -->页码 = 跳过的数量//每页数量+1
    page = skip // limit + 1
    #print(skip, limit, page)
    cache_list = await get_cached_list(category_id,page,limit)
    if cache_list:
        #需要orm类型
        return [News(**item) for item in cache_list]
    rule = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(rule)
    news_list = result.scalars().all()
    if news_list:
        news_list = jsonable_encoder(news_list)
        """
        方法2：先把orm数据转换为字典才能写入缓存
              orm转成Pydantic ,再转为字典
              by_alias=Fase 不使用别名，保存Python 风格 因为Redis数据是给后端的
              new_list = [NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=Fase) for item in news_list]
        """
        await set_cached_list(category_id,skip,limit,news_list)
    return news_list
#h获取分类下新闻总数
async def get_news_count(db: AsyncSession,category_id: int):
    rule = select(func.count(News.category_id)).where(News.category_id == category_id)
    result = await db.execute(rule)
    return result.scalar_one()
#查询详细详细新闻内容
async def get_news_detail(db: AsyncSession,news_id: int):
    rule = select(News).where(News.id == news_id)
    result = await db.execute(rule)
    return result.scalar_one_or_none()
#实时更新浏览量
async def add_news_view(db, news_id: int):
    """
    新闻浏览量 +1
    :param db: 异步数据库会话
    :param news_id: 新闻id
    """
    # update语句：views = views + 1，数据库自增，避免并发冲突
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    # 返回是否成功更新到新闻 rowcount 获取 SQL 语句影响的数据行数。
    return result.rowcount >0

#查询相关新闻
async def get_related_news(db, category_id: int, self_id: int, limit: int = 5):
    """
    获取同分类相关新闻
    :param db: 数据库会话
    :param category_id: 当前新闻分类ID
    :param self_id: 当前新闻ID，排除自己
    :param limit: 推荐条数，默认3条
    :return: 新闻列表ORM对象
    """
    #\Python 代码换行续行符
    stmt = select(News)\
        .where(News.category_id == category_id,News.id != self_id)\
        .order_by(News.views.desc(), News.publish_time.desc())\
        .limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "image": news_detail.image,
        "publishTime": news_detail.publish_time
    }
    for news_detail in result.scalars().all()]
