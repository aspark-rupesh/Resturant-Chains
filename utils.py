import json
import hashlib
import pathlib
BASE_DIR = pathlib.Path(__name__).parent.resolve()
def prepare_store_data(obj_dict,keys=[]):
    data = {}
    for key in keys:
        try:
            data[key] = obj_dict[key]
        except:
            pass
    return data


def get_hash(obj):
    """
    Generate a hash for a JSON object.
    """
    obj_str = json.dumps(obj, sort_keys=True)
    return hashlib.sha256(obj_str.encode()).hexdigest()


def export_product_file(id,product,product_customization_id_list,base_product_data):
    data = prepare_store_data(product,["product_id","name","unit_size","unit_of_measurement","description","delivery_price"
                                                             , "pickup_price","delivery_min_price","pickup_min_price","formatted_price",
                                                              "should_fetch_customizations","supports_image_scaling"])
    data["product_customization_id"] = [product_customization_id for product_customization_id in product_customization_id_list]
    data.update(base_product_data)
    
    

    with open(f'{BASE_DIR}/products/{id}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)