import pymongo


client = pymongo.MongoClient()
db = client.reciter


i = db.users.find({'username': 'PeterLu'})
i['admin'] = True
db.users.update({'username': 'PeterLu'}, i)