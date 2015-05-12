from mongo_single import Mongo

res = Mongo.get().projects.find({'name': '321'}, {'_id': 0})
print res
res[0]
for i in Mongo.get().projects.find({}, {'_id': 0})[0]:
    print i
