import pymongo
import uuid


client = pymongo.MongoClient()
db = client.reciter

'''
    集合名 yule

    id 游戏id
    name 游戏名
    hot 游戏热度
    path 游戏html文件路径
    intro 游戏介绍
    timef 创建时间
    creator 创建者
'''


l = list(db.yule.find())
for i in l:
     db.yule.delete_one({'name': i['name']})
for i in gamelist:
     db.yule.insert_one(i)