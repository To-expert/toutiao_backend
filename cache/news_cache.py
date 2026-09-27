#获取或存储相关新闻缓存和存储
from typing import List, Dict, Any, Optional

from config.cache_conf import get_cache, set_cache, get_json_cache
#KEY
CATEGORIES_KEY = "news:categories"
NEWS_LIST_KEY = "news:list"
#获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)
#写入新闻分类缓存
#分类，配置：7200 ，列表：600，详情：1800，验证码：120---数据越稳定越持久
async def set_cached_categories(data: List[Dict[str, Any]],expire: int = 7200):
    return await set_cache(CATEGORIES_KEY,data,expire)
#获取新闻列表缓存
async def get_cached_list(category_id: Optional[int],page: int, page_size: int ):
    category_part = category_id if category_id is not None else "all"
    #print(category_id, page, page_size)
    key = f"{NEWS_LIST_KEY}:{category_part}:{page}:{page_size}"
    return await get_json_cache(key)
#写入新闻列表-缓存
#key = news_list:分类id:页码:每页数量:+列表数据+过期时间
async def set_cached_list(category_id: Optional[int],page: int, page_size: int ,data: List[Dict[str, Any]],expire: int = 1800):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_KEY}{category_part}:{page}:{page_size}"
    return await set_cache(key,data,expire)


