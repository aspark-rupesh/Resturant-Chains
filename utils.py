import json
import hashlib
def prepare_store_date(obj_dict,keys=[]):
    data = {}
    for key in keys:
        try:
            data[key] = obj_dict[key]
        except:
            print("exception")
            pass
    return data


def get_hash(obj):
    """
    Generate a hash for a JSON object.
    """
    obj_str = json.dumps(obj, sort_keys=True)
    return hashlib.sha256(obj_str.encode()).hexdigest()

