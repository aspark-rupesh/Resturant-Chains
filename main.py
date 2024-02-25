from fastapi import FastAPI
from db_connection import db
import json
from bson import json_util,ObjectId
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
def product_detail(product_id : int = None,):
    customization_list = []

    if product_id:
        #  get the product document
        product = db.products.find_one({"product_id":product_id},{"_id":False})

        # get product_customization documents related to this product
        customizations = db.product_customization.find({"product_id":product_id})

        print("here")
        print(customizations)


        # prepare the customization list along with its options
        for customization in customizations:
            print("cust obj>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<,,")
            #  get the customization document
            customization_object = db.customizations.find_one({"_id":customization["customization_id"]},{"_id":False})
            
            print(customization_object)

            #get all option documents related to this product_customization
            options = db.options.find({"_id":{'$in':customization["options"]}},{"_id":False})
            customization_json = json.loads(json_util.dumps(customization_object))

            # add options in the customization_json
            customization_json["options"] = json.loads(json_util.dumps(options))
            customization_list.append(customization_json)
        
        # get the base product of this product
        base_product = db.base_products.find_one({'_id':ObjectId(product["base_product"])},{"_id":False})

        # prepare the data_json to be returned
        data_json=json.loads(json_util.dumps(product))
        data_json ["cusomizations"] =  customization_list
        data_json.update(base_product)
        return {"product":data_json}