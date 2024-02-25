import pandas as pd
from utils import  prepare_store_date
from db_connection import db
import pathlib

BASE_DIR = pathlib.Path(__name__).parent.resolve()


file_names = ["one.json","two.json","three.json"]

unique_options = []
unique_customizations = []
duplixate_option_count = 0
option_id = 1

# loop through the files
for file_name in file_names:
    data = pd.read_json(f"{BASE_DIR}/{file_name}")

    #get all stores
    print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<,Loading data t the database of file {file_name}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    # get the generator for stores in this file
    stores = (store for store in data["stores"])
    for store in stores:
        store_name = store["name"]
        print(store["name"])

        # generator for menus of the individual store
        menus = (menu for menu in store["menus"])

        # loop through the menus
        for menu in menus:
            categories = (category for category in menu["categories"])
            for cat in categories:
                menu_items = (menu_item for menu_item in cat["menu_item_list"])
                for menu_item in menu_items:
                    # prepare a dictionary for this menu item
                    product_data = prepare_store_date(menu_item,["name","unit_size","unit_of_measurement","description","delivery_price"
                                                             ,"delivery_min_price","pickup_min_price","product_id","formatted_price","should_fetch_customizations","supports_image_scaling"])
                    product_data["store"] = store_name
                    # insert into db on products collection
                    created_product_id = db.products.insert_one(product_data).inserted_id

                    # get the product_id for further uses (creating product_customization document)
                    product_id = menu_item["product_id"]

                    #get customizations generator
                    customizations = (customization for customization in menu_item["customizations"])

                    # loop through the generator to get customizations of the menu_item 
                    for customization in customizations:
                        # prepare dictionary for thr customization 
                        customization_data = prepare_store_date(customization,["name","min_choice_options","max_choice_options"])

                        if customization_data not in unique_customizations:
                            # no such customization has been created with the given dictionary.
                            #  Add it to the unique_customizations list (to determine this customization has already been created)
                            unique_customizations.append(customization_data)

                            # insert into database on customizations collection.
                            created_customization = db.customizations.insert_one(customization_data.copy())
                            customization_id = created_customization.inserted_id
                        else:
                            # customization document is available with the provided dictionary, retrieve its id for further use
                            customization_id = db.customizations.find_one(customization_data)["_id"]

                        # create a generator for options of this customization                      
                        options = (option for option in customization["options"])   
                        option_id_list = []

                        # loop through the options generator  
                        for option in options:
                            # prepare dictionary for this option
                            option_data = prepare_store_date(option,["name","price","min_qty","max_qty","conditional_price","formatted_price","default_qty"])

                            if option_data not in unique_options:
                                # this option is never been created, so create one
                                unique_options.append(option_data)
                                created_option = db.options.insert_one(option_data.copy())
                                option_id = created_option.inserted_id
                            else:
                                # this option has already been created, get its id
                                duplixate_option_count += 1
                                option_id = db.options.find_one(option_data)["_id"]
                            
                            # append the option_id to create a list of option_ids shared by this customization 
                            option_id_list.append(option_id)

                        # insert a product_customization document with the prepared data. This is later used to determine customization and its options of a particular product.               
                        db.product_customization.insert_one({
                            "product_id": product_id,
                            "customization_id" : customization_id,
                            "options" : option_id_list
                        })
                        
                            

    print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Successfully Loaded data for {file_name}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")

