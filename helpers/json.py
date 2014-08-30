from bson.objectid import ObjectId

def jsonhandler(obj):
    if hasattr(obj, 'jsonable'):
        return obj.jsonable()
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, ObjectId):
        return str(ObjectId)
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))
