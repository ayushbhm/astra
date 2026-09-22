import redis
import json
from functools import wraps
from flask import jsonify, request


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


def cache_response(timeout=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            print("DECORATOR CALLED")   # <-- new line, added here

            cache_key = f"cache:{f.__name__}:{request.query_string.decode()}"
            cached_response = redis_client.get(cache_key)

            if cached_response:
                return jsonify(json.loads(cached_response))

            response = f(*args, **kwargs)
            redis_client.setex(cache_key, timeout, json.dumps(response.get_json()))
            return response

        return decorated_function
    return decorator