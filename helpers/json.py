from bson.objectid import ObjectId

def jsonhandler(obj):
    if hasattr(obj, 'jsonable'):
        return obj.jsonable()
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        raise TypeError
