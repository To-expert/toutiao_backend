import json
import redis.asyncio as redis
"""setex: key:str
          expire:int(设置缓存过期时间)
          vaule:str
    get： key:str(获取缓存值，若不存在，返回none)
    delete: key:str(删除指定的缓存键)
    exists: key:str(检查缓存键是否存在，返回值为：bool类型)"""
#创建redis连接对象
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
redis_client = redis.Redis(host=REDIS_HOST, #redis主机地址
                           port=REDIS_PORT, #redis端口
                           db=REDIS_DB,     #redis数据库编号，0~15
                           decode_responses=True,#是否将字节转换为字符串
                           protocol=2) #解决Windows Redis HELLO命令报错
#设置和读取（字符串 和 列表或字典）
#读取字符串
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None
#读取列表或字符串
async def get_json_cache(key: str):
   try:
       date = await redis_client.get(key)
       if date:
           return json.loads(date)  #把 Redis 拿到的JSON 字符串，转回 Python 字典 / 列表对象返回
       return None
   except Exception as e:
       print(f"获JSON取缓存失败：{e}")
    #设置缓存
async def set_cache(key: str, value,expire:int = 3600):
   try:
       if isinstance(value,(list,dict)):
           # 转字符串
           json_str = json.dumps(value,ensure_ascii=False)
       else:
           json_str = value
       await redis_client.setex(key,expire,json_str)
       return True
   except Exception as e:
       print(f"设置缓存失败：{e}")
       return False


