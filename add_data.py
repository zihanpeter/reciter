import pymongo


client = pymongo.MongoClient()
db = client.reciter

dics = list(db.users.find())

for i in dics:
    i['intro'] = 'Nothing'
    db.users.update({'username': i['username']}, i)