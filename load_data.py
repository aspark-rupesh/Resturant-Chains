import pandas as pd
from utils import  export_product_file, get_hash, prepare_store_data
from db_connection import db, reset_database
from utils import BASE_DIR



file_names = ["one.json","two.json","three.json"]

unique_options = {}
unique_customizations = {}
unique_base_products = {}
option_id = 1
product_id_index = 1

# drop the database
reset_database(db)

# loop through the files
for file_name in file_names:
    data = pd.read_json(f"{BASE_DIR}/{file_name}")

    print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<,Loading data t the database of file {file_name}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    # get the generator for stores in this file
    stores = (store for store in data["stores"])
    for store in stores:
        store_name = store["name"]
        print(store["name"])

        # prepare a dictionary with data of this store
        store_data = prepare_store_data(store,[
            "name","address","type","description","local_hours","cuisines","food_photos","logo_photos","store_photos",
            "dollar_signs", "pickup_enabled","delivery_enabled","offers_first_party_delivery","offers_third_party_delivery",
            "weighted_rating_value","aggregated_rating_count","supports_upc_codes","is_open"
        ])

        # insert into database
        store_id = db.stores.insert_one(store_data).inserted_id


        # generator for menus of the individual store
        menus = (menu for menu in store["menus"])

        # loop through the menus
        for menu in menus:
            categories = (category for category in menu["categories"])
            for cat in categories:
                menu_items = (menu_item for menu_item in cat["menu_item_list"])
                for menu_item in menu_items:

                    # prepare data dictionary for base_product
                    base_product_data = prepare_store_data(menu_item,["name","unit_size","unit_of_measurement","description","delivery_price"
                                                             , "pickup_price","delivery_min_price","pickup_min_price","formatted_price",
                                                              "should_fetch_customizations","supports_image_scaling"])
                    
                    # get a hash value of the dictionary
                    base_product_hash = get_hash(base_product_data)

                    if base_product_hash not in unique_base_products:
                        # no such base_product has been created with the given dictionary.
                        # get a hash and add it to the unique_base_products dict storing the base_product_id

                        # insert into database on base_products collection.
                        created_base_product = db.base_products.insert_one(base_product_data.copy())
                        base_product_id = created_base_product.inserted_id

                        unique_base_products[base_product_hash] = base_product_id

                    else:
                        # base_product document is available with the provided hash, retrieve its id for further use
                        base_product_id = unique_base_products[base_product_hash]
                    product_data = {}
                    product_data["base_product"] = str(base_product_id)
                    product_data["store"] = store_name
                    product_data["store_id"] = str(store_id)
                    product_data["product_id"] = product_id_index


                    # insert into db on products collection
                    created_product_id = db.products.insert_one(product_data.copy()).inserted_id

                    # get the product_id for further uses (creating product_customization document)
                    product_id = created_product_id

                    #get customizations generator
                    customizations = (customization for customization in menu_item["customizations"])
                    product_customization_id_list= []

                    # loop through the generator to get customizations of the menu_item 
                    for customization in customizations:
                        # prepare dictionary for thr customization 
                        customization_data = prepare_store_data(customization,["name","min_choice_options","max_choice_options"])
                        customization_hash_key = get_hash(customization_data)

                        if customization_hash_key not in unique_customizations:
                            # no such customization has been created with the given dictionary.
                            # get a hash and add it to the unique_customizations dict storing the customization id

                            # insert into database on customizations collection.
                            created_customization = db.customizations.insert_one(customization_data.copy())
                            customization_id = created_customization.inserted_id

                            unique_customizations[customization_hash_key] = customization_id

                        else:
                            # customization document is available with the provided hash, retrieve its id for further use
                            customization_id = unique_customizations[customization_hash_key]

                        # create a generator for options of this customization                      
                        options = (option for option in customization["options"])   
                        option_id_list = []

                        # loop through the options generator  
                        for option in options:
                            # prepare dictionary for this option
                            option_data = prepare_store_data(option,["name","price","min_qty","max_qty","conditional_price","formatted_price","default_qty"])

                            option_hash_key = get_hash(option_data)

                            if option_hash_key not in unique_options:
                                # this option is never been created, so create one
                                created_option = db.options.insert_one(option_data.copy())
                                option_id = created_option.inserted_id

                                # add the hash key with option_id as its value in the unique_options dictionary
                                unique_options[option_hash_key] = option_id
                            else:
                                # this option has already been created, get its id
                                option_id = unique_options[option_hash_key]
                            
                            # append the option_id to create a list of option_ids shared by this customization 
                            option_id_list.append(option_id)

                        # insert a product_customization document with the prepared data. This is later used to determine customization and its options of a particular product.               
                        product_customization_id = db.product_customization.insert_one({
                                                "product_id": product_id_index,
                                                "customization_id" : customization_id,
                                                "options" : option_id_list
                                            }).inserted_id
                        product_customization_id_list.append(str(product_customization_id))

                    export_product_file(product_id_index,menu_item,product_customization_id_list,product_data)
                    product_id_index += 1

                
                        
                            

    print(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Successfully Loaded data for {file_name}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")

