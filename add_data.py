from pymongo import MongoClient
from gridfs import GridFS


# 连接到MongoDB
client = MongoClient()
db = client.forum

# 创建GridFS实例
fs = GridFS(db)

# 查找数据
file = fs.find()

print(file)
