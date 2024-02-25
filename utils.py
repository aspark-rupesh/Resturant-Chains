def prepare_store_date(obj_dict,keys=[]):
 
    data = {}
    for key in keys:
        try:
            data[key] = obj_dict[key]
        except:
            print("exception")
            pass
    return data



