##########################################################################################
################### Autumn Alien
##########################################################################################



##########################################################################################
####### Importing libraries
##########################################################################################

from deta import Deta
from fastapi import  FastAPI
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from geopy.geocoders import Nominatim


# calling the nominatim tool
geoLoc = Nominatim(user_agent="GetLoc")

import uvicorn

app = FastAPI()

#### Home route

@app.get('/',tags = ['Home'])
async def home():
    return 'home'

##########################################################################################
######## Authorisation and initialising database
#########################################################################################

deta_base_key = 'your deta database key'
deta = Deta(deta_base_key)

shops = deta.Base('Shops5')

goods = deta.Base('Goods5')

transactions_history = deta.Base('Transactions_history')
price_history = deta.Base('Price_history')

shops_open = deta.Base('Shops_open')
shops_operations = deta.Base('Shops_operations')

quantity_history1 = deta.Base('Quantity_history') 

@app.get('/Get_shops_general/',tags = ['Search'])
async def Get_shops_general():
    
    try:
        
        return shops.fetch({'operations_status':'operational'})._items
    
    except Exception:
        
        return 'error'    
    

@app.get('/Get_goods_general/',tags = ['Search'])
async def Get_goods_general():
    
    try:
        
        return goods.fetch({'shop_operations_status':'operational'})._items
    
    except Exception:
        
        return 'error'
    

@app.get('/Shops_info_all',tags = ['Search'])
async def Shops_info_all():
    
    try:
        
            
        shops_list = []
        
        for i in  shops.fetch({'operations_status':'operational'})._items:
            
            goods_list = []
            
            for k in goods.fetch({'national_id':i['national_id'],'shop_name':i['shop_name'],'shop_operations_status':'operational'})._items:
                
                transactions_history_list = transactions_history.fetch({'national_id':k['national_id'],'product_unique_name':k['unique_name']})._items
                price_history_list = price_history.fetch({'national_id':k['national_id'],'product_unique_name':k['unique_name']})._items
                
                product_dict = {'product':k,'transactions_history':transactions_history_list,'price_history':price_history_list}
                
                goods_list.append(product_dict)
                
            shops_open_list = shops_open.fetch({'national_id':i['national_id'],'shop_name':i['shop_name']})._items        
            shops_operations_list = shops_operations.fetch({'national_id':i['national_id'],'shop_name':i['shop_name']})._items
               
            shop_dict = {'Shop':i,'Goods':goods_list,'Open_history':shops_open_list,'Operations_history':shops_operations_list}
            
            shops_list.append(shop_dict)
            
        return shops_list
 
        
    except Exception:
        
        return 'error'
    
    
@app.get('/Search_by_product/',tags = ['Search'])
async def Search_by_product(product_name : str):
    
    try:
        
        shops_list = []
        
        for i in  shops.fetch({'operations_status':'operational'})._items:
            
            goods_list = []
            
            for k in goods.fetch({'national_id':i['national_id'],'shop_name':i['shop_name'],'shop_operations_status':'operational','name':product_name.lower()})._items:
                
                transactions_history_list = transactions_history.fetch({'national_id':k['national_id'],'product_unique_name':k['unique_name']})._items
                price_history_list = price_history.fetch({'national_id':k['national_id'],'product_unique_name':k['unique_name']})._items
                
                product_dict = {'product':k,'transactions_history':transactions_history_list,'price_history':price_history_list}
                
                goods_list.append(product_dict)
                
            shops_open_list = shops_open.fetch({'national_id':i['national_id'],'shop_name':i['shop_name']})._items        
            shops_operations_list = shops_operations.fetch({'national_id':i['national_id'],'shop_name':i['shop_name']})._items
            
            if len(goods_list) == 0:
                return 'not available'
            
            shop_dict = {'Shop':i,'Goods':goods_list,'Open_history':shops_open_list,'Operations_history':shops_operations_list}
            
            shops_list.append(shop_dict)
            
        return shops_list
        
    except Exception:
        
        return 'error'
    
    
@app.get('/Search_by_location/',tags = ['Search'])
async def Search_by_location(location : str):
    
    try:
        
        shops_list = []
        
        for i in  shops.fetch({'operations_status':'operational'})._items:
            
            latitude = i['latitude']
            longtude = i['longtude']
            
            locname = geoLoc.reverse("{},{}".format(latitude,longtude))
            
            if location.lower() in locname.address.lower():
            
                goods_list = []
                
                for k in goods.fetch({'national_id':i['national_id'],'shop_name':i['shop_name'],'shop_operations_status':'operational'})._items:
                    
                    transactions_history_list = transactions_history.fetch({'national_id':k['national_id'],'product_unique_name':k['unique_name']})._items
                    price_history_list = price_history.fetch({'national_id':k['national_id'],'product_unique_name':k['unique_name']})._items
                    
                    product_dict = {'product':k,'transactions_history':transactions_history_list,'price_history':price_history_list}
                    
                    goods_list.append(product_dict)
                    
                shops_open_list = shops_open.fetch({'national_id':i['national_id'],'shop_name':i['shop_name']})._items        
                shops_operations_list = shops_operations.fetch({'national_id':i['national_id'],'shop_name':i['shop_name']})._items
                
                if len(goods_list) == 0:
                    return 'not available'
                
                shop_dict = {'Shop':i,'Goods':goods_list,'Open_history':shops_open_list,'Operations_history':shops_operations_list}
                
                shops_list.append(shop_dict)
            
        return shops_list
        
    except Exception:
        
        return 'error'
    
    
    
@app.get('/Search_by_location_product/',tags = ['Search'])
async def Search_by_location_product(location : str ,product_name : str ):
    
    try:
        
        shops_list = []
        
        for i in  shops.fetch({'operations_status':'operational'})._items:
            
            latitude = i['latitude']
            longtude = i['longtude']
            
            locname = geoLoc.reverse("{},{}".format(latitude,longtude))
            
            if location.lower() in locname.address.lower():
            
                goods_list = []
                
                for k in goods.fetch({'national_id':i['national_id'],'shop_name':i['shop_name'],'shop_operations_status':'operational','name':product_name.lower()})._items:
                    
                    transactions_history_list = transactions_history.fetch({'national_id':k['national_id'],'product_unique_name':k['unique_name']})._items
                    price_history_list = price_history.fetch({'national_id':k['national_id'],'product_unique_name':k['unique_name']})._items
                    
                    product_dict = {'product':k,'transactions_history':transactions_history_list,'price_history':price_history_list}
                    
                    goods_list.append(product_dict)
                    
                shops_open_list = shops_open.fetch({'national_id':i['national_id'],'shop_name':i['shop_name']})._items        
                shops_operations_list = shops_operations.fetch({'national_id':i['national_id'],'shop_name':i['shop_name']})._items
                
                if len(goods_list) == 0:
                    return 'not available'
                
                shop_dict = {'Shop':i,'Goods':goods_list,'Open_history':shops_open_list,'Operations_history':shops_operations_list}
                
                shops_list.append(shop_dict)
            
        return shops_list
        
    except Exception:
        
        return 'error'
    
def store_quantity_database():
        
    date = str(datetime.today())
    
    for i in goods.fetch({'shop_operations_status':'operational'})._items:
        
        latitude = i['shop_latitude']
        longtude = i['shop_longtude']
        
        locname = geoLoc.reverse("{},{}".format(latitude,longtude))
        
        quantity_history1.put({'product_name':i['name'],'quantity':i['quantity'],'date':date,'shop_seller':i['seller'],'shop_name':i['shop_name'],'location':locname.address.lower()})
        
        
        
sched = BackgroundScheduler(daemon=True)
sched.add_job(store_quantity_database,'interval',hours = 24)
sched.start()
    
@app.get('/Search_quantity_history/',tags = ['Search'])
async def Search_quantity_history(location : str,product_name : str):
    
    try:
        
        
        quantity_history = deta.Base('Quantity_history') 
        
        quantity_history_list = []
        
        for i in quantity_history.fetch({'product_name':product_name.lower()})._items:
    
            if location.lower() in i['location']:
                
                quantity_history_list.append({'date':i['date'],'product_name':i['product_name'],'quantity':i['quantity']})
                
        
        dates_list = []
        
        for j in quantity_history_list:
            dates_list.append(j['date'])
            
        dates_list = list(set(dates_list))
        
        quantity_history_final = []
        
        for k in dates_list:
            
            date_quantity = []
            
            for n in quantity_history_list:
                
                if n['date'] == k:
                    
                    date_quantity.append(n['quantity'])
            
            quantity_history_final.append({'date':k,'product_name':product_name.lower(),'quantity':sum(date_quantity)})
            
        return quantity_history_final
        
        
        
    except Exception:
        
        return 'error'

if __name__ == '__main__':
    uvicorn.run('app:app',reload = True)
    