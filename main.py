from fastapi import FastAPI, Request, Response
from db_connection import db
import json
from bson import json_util
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/api/product/")
def product_detail(product_id : str = None,):
    customization_list = []

    if product_id:
        product = db.products.find_one({"product_id":product_id},{"_id":False})

        customizations = db.product_customization.find({"product_id":product_id})

        for customization in customizations:
            customization_object = db.customizations.find_one({"_id":customization["customization_id"]},{"_id":False})    
            options = db.options.find({"_id":{'$in':customization["options"]}},{"_id":False})
            customization_json = json.loads(json_util.dumps(customization_object))
            customization_json["options"] = json.loads(json_util.dumps(options))
            customization_list.append(customization_json)
            
        data_json=json.loads(json_util.dumps(product))
        data_json ["cusomizations"] =  customization_list

        return {"product":data_json}