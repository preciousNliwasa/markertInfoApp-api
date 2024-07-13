##########################################################################################
################### Autumn Alien
##########################################################################################



##########################################################################################
####### Importing libraries
##########################################################################################

from deta import Deta

from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status,Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

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

account_details = deta.Base('AccountsClive5')

shops = deta.Base('Shops5')

goods = deta.Base('Goods5')

transactions_history = deta.Base('Transactions_history')
price_history = deta.Base('Price_history')

shops_open = deta.Base('Shops_open')
shops_operations = deta.Base('Shops_operations')

def account_dict_func():
    
    global admin_db
    
    accounts_list = account_details.fetch()._items

    account_dict = {}

    for i in accounts_list:
        account_dict[i['username']] =  i

    admin_db = account_dict
    
sched = BackgroundScheduler(daemon=True)
sched.add_job(account_dict_func,'interval',seconds = 3)
sched.start()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    phone_number: Union[str, None] = None
    account_status: Union[str, None] = None
    full_name: Union[str, None] = None
    gender: Union[str, None] = None
    district: Union[str, None] = None
    town: Union[str, None] = None
    national_id: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def decode_token(token):
    user = get_user(admin_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/token",tags = ['Log In'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = admin_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    password_ = form_data.password
    if not password_ == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}

######################################################################################
########## 
######################################################################################
def hex_token(text):
    
    return text.encode('utf-8').hex()

def from_hex(token):
    
    return bytes.fromhex(token).decode('utf-8')


######################################################################################
########## Account Functions
######################################################################################

@app.post('/Create_an_account/',tags = ['Accounts'])
async def Create_an_account(user_name : str = Form(...),gender : str = Form(...),DoB : str = Form(...),district : str = Form(...),town : str = Form(...),email : str = Form(...),phone_number : str = Form(...),national_id : str = Form(...),password : str = Form(...)):
    
    try:
        
        for i in account_details.fetch()._items:
            if i['national_id'] == hex_token(national_id):
                return 'national id asscociated with another account'
            
        
        return account_details.put({'username':user_name,'full_name':user_name,'gender' : gender,'DoB':DoB,'district': district,'town':town,'email':email,'phone_number':phone_number,'national_id':hex_token(national_id),'hashed_password':password,'date_created':str(datetime.today()),'account_status':'active'})
    
    except Exception:
        
        return 'error'


@app.get('/Get_accounts/',tags = ['Accounts'])
async def Get_accounts(current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            return account_details.fetch({'hashed_password':current_user.hashed_password})._items
        
        return 'account not verified'
    
    except Exception:
        
        return 'error'


@app.post('/Create_shop/',tags = ['Set shop'])
async def Create_shop(shop_name : str = Form(...),description : str = Form(...),location : str = Form(...),latitude : str = Form(...),longtude : str = Form(...),current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            for i in account_details.fetch()._items:
                if i['hashed_password'] == current_user.hashed_password:

                    for k in shops.fetch()._items:
                        if k['national_id'] == current_user.national_id:
                            if k['shop_name'] == shop_name:
                                return 'already created'
                            
                        if (k['latitude'] == latitude) & (k['longtude'] == longtude):
                            return 'location already occupied'
                     
                    date = str(datetime.today()) 
                    shops_operations.put({'owner':current_user.full_name,'national_id':current_user.national_id,'shop_name':shop_name,'status':'operational','date':date})
                    shops_open.put({'owner':current_user.full_name,'national_id':current_user.national_id,'shop_name':shop_name,'status':'closed','date':date})
                    return shops.put({'owner':current_user.full_name,'shop_name':shop_name,'description':description,'location':location,'latitude':latitude,'longtude':longtude,'status':'closed','operations_status':'operational','date_created':date,'national_id':current_user.national_id})
    
            return 'create account' 
        
        return 'account not verified'
    
    except Exception:
        
        return 'error' 
    
@app.get('/Get_shops/',tags = ['Shop details'])
async def Get_shops(current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            return shops.fetch({'national_id':current_user.national_id})._items
            
        return 'verify your account'
    
    except Exception:
        
        return 'error'

@app.post('/open_shop_operations/',tags = ['Shop operations'])
async def Open_shop_operations(shop_name : str = Form(...),current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            for y in shops.fetch({'national_id':current_user.national_id,'operations_status':'not operational'})._items:
                if y['shop_name'] == shop_name:
                    key = y['key']
                    
                    shops_operations.put({'owner':current_user.full_name,'national_id':current_user.national_id,'shop_name':shop_name,'status':'operational','date':str(datetime.today())})
                    
                    for k in goods.fetch({'national_id':current_user.national_id})._items:
                        if k['shop_name'] == shop_name:
                            key2 = k['key']
                            
                            goods.put({'seller':current_user.full_name,'unique_name':k['unique_name'],'name':k['name'],'description':k['description'],'price':k['price'],'quantity':k['quantity'],'method_of_payment':k['method_of_payment'],'shop_name':k['shop_name'],'shop_location':k['shop_location'],'shop_latitude':k['shop_latitude'],'shop_longtude':k['shop_longtude'],'shop_description':k['shop_description'],'shop_operations_status':'operational','date_created':k['date_created'],'national_id':current_user.national_id},key2)
                            
                    
                    return shops.put({'owner':current_user.full_name,'shop_name':shop_name,'description':y['description'],'location':y['location'],'latitude':y['latitude'],'longtude':y['longtude'],'status':y['status'],'operations_status':'operational','date_created':y['date_created'],'national_id':current_user.national_id},key)
                    
                    
            return 'shop not available or already in operations'
        
    except Exception:
        
        return 'error'
        
@app.post('/Close_shop_operations/',tags = ['Shop operations'])
async def Close_shop_operations(shop_name : str = Form(...),current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            for y in shops.fetch({'national_id':current_user.national_id,'operations_status':'operational'})._items:
                if y['shop_name'] == shop_name:
                    key = y['key']
                    
                    shops_operations.put({'owner':current_user.full_name,'national_id':current_user.national_id,'shop_name':shop_name,'status':'not operational','date':str(datetime.today())})
                    
                    for k in goods.fetch({'national_id':current_user.national_id})._items:
                        if k['shop_name'] == shop_name:
                            key2 = k['key']
                            
                            goods.put({'seller':current_user.full_name,'unique_name':k['unique_name'],'name':k['name'],'description':k['description'],'price':k['price'],'quantity':k['quantity'],'method_of_payment':k['method_of_payment'],'shop_name':k['shop_name'],'shop_location':k['shop_location'],'shop_latitude':k['shop_latitude'],'shop_longtude':k['shop_longtude'],'shop_description':k['shop_description'],'shop_operations_status':'not operational','date_created':k['date_created'],'national_id':current_user.national_id},key2)
                    
                    return shops.put({'owner':current_user.full_name,'shop_name':shop_name,'description':y['description'],'location':y['location'],'latitude':y['latitude'],'longtude':y['longtude'],'status':y['status'],'operations_status':'not operational','date_created':y['date_created'],'national_id':current_user.national_id},key)
                    
                    
            return 'shop not available or already not operational'
            
        
    except Exception:
        
        return 'error'


@app.post('/Create_goods/',tags = ['Products'])
async def Create_goods(shop_name : str = Form(...),unique_name : str = Form(...),name : str = Form(...),description : str = Form(...),price : float = Form(...),quantity : int = Form(...),method_of_payment : str = Form(...),current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
       

            for k in goods.fetch({'national_id':current_user.national_id})._items:
                if k['unique_name'] == hex_token(unique_name):
                    return 'unique_product_name already created'
            
            for y in shops.fetch({'national_id':current_user.national_id,'operations_status':'operational'})._items:
                if y['shop_name'] == shop_name:
                    
                    if quantity >= 0:
                        
                        date = str(datetime.today()) 
                        
                        transactions_history.put({'seller':current_user.full_name,'national_id':current_user.national_id,'product_unique_name':hex_token(unique_name),'product_name':name,'price':abs(price),'quantity':abs(quantity),'shop_name':shop_name,'transaction_type':'initial_stock','by':abs(quantity),'transaction_date':date})
                        price_history.put({'seller':current_user.full_name,'national_id':current_user.national_id,'product_unique_name':hex_token(unique_name),'product_name':name,'price':abs(price),'price_date':date,'type':'initial'})
                        
                        return goods.put({'seller':current_user.full_name,'unique_name':hex_token(unique_name),'name':name,'description':description,'price':abs(price),'quantity':abs(quantity),'method_of_payment':method_of_payment,'shop_name':y['shop_name'],'shop_location':y['location'],'shop_latitude':y['latitude'],'shop_longtude':y['longtude'],'shop_description':y['description'],'shop_operations_status':'operational','date_created':date,'national_id':current_user.national_id})
    
                    else:
                        return 'quantity cannot be negative'
                        
            return 'shop not available or not operational'
        
        return 'account not verified'
    
    except Exception:
        
        return 'error' 
    

@app.get('/Get_goods/',tags = ['Products'])
async def Get_goods(current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            return goods.fetch({'national_id':current_user.national_id})._items
            
        return 'verify your account'
    
    except Exception:
        
        return 'error'
    

@app.get('/generate_qr_code/',tags = ['QR'])
async def generate_qr_code(unique_name : str,current_user: User = Depends(get_current_user)):
       
    try:
        
        if current_user.account_status == 'active':
 
            for k in goods.fetch({'national_id':current_user.national_id,'unique_name':unique_name,'shop_operations_status':'operational'})._items:
                code = k['unique_name'] + '<0000>' + current_user.national_id
                return hex_token(code)
            
    
            return 'product not available or shop not operational' 
        
        return 'account not verified'
    
    except Exception:
        
        return 'error'
    
    
@app.get('/Show_unique_name/',tags = ['QR'])
async def Show_unique_name(unique_code,current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            
            if goods.fetch({'national_id':current_user.national_id,'unique_name':unique_code,'shop_operations_status':'operational'})._items:
                return from_hex(unique_code)
            
            return 'name not available'
        
    except Exception:
        
        return 'error'
    
@app.post('/Open_shop/',tags = ['Check in'])
async def Open_shop(shop_name : str,current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            for y in shops.fetch({'national_id':current_user.national_id,'status' : 'closed','operations_status':'operational'})._items:
                if y['shop_name'] == shop_name:
                    key = y['key']
                    
                    shops_open.put({'owner':current_user.full_name,'national_id':current_user.national_id,'shop_name':shop_name,'status':'opened','date':str(datetime.today())})
                    
                    return shops.put({'owner':current_user.full_name,'shop_name':shop_name,'description':y['description'],'location':y['location'],'latitude':y['latitude'],'longtude':y['longtude'],'status':'opened','operations_status':y['operations_status'],'date_created':y['date_created'],'national_id':current_user.national_id},key)    
                    
            return 'shop not available or already opened or not operational'
    
    except Exception:
        
        return 'error'
    
@app.post('/Close_shop/',tags = ['Check in'])
async def Close_shop(shop_name : str,current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            for y in shops.fetch({'national_id':current_user.national_id,'status':'opened','operations_status':'operational'})._items:
                if y['shop_name'] == shop_name:
                    key = y['key']
                    
                    shops_open.put({'owner':current_user.full_name,'national_id':current_user.national_id,'shop_name':shop_name,'status':'closed','date':str(datetime.today())})
                    
                    return shops.put({'owner':current_user.full_name,'shop_name':shop_name,'description':y['description'],'location':y['location'],'latitude':y['latitude'],'longtude':y['longtude'],'status':'closed','operations_status':y['operations_status'],'date_created':y['date_created'],'national_id':current_user.national_id},key)  
                    
            return 'shop not available or already closed or not operational'
    
    except Exception:
        
        return 'error'
    
    
@app.put('/update_price/',tags = ['Price'])
async def Update_price(unique_name : str = Form(...),new_price : float = Form(...),current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            for k in goods.fetch({'national_id':current_user.national_id,'shop_operations_status':'operational'})._items:
                if k['unique_name'] == unique_name:
                    key = k['key']
                    
                    price_history.put({'seller':current_user.full_name,'national_id':current_user.national_id,'product_unique_name':unique_name,'product_name':k['name'],'price':abs(new_price),'price_date':str(datetime.today()),'type':'updated'})
                
                    return goods.put({'seller':current_user.full_name,'unique_name':unique_name,'name':k['name'],'description':k['description'],'price':abs(new_price),'quantity':k['quantity'],'method_of_payment':k['method_of_payment'],'shop_name':k['shop_name'],'shop_location':k['shop_location'],'shop_latitude':k['shop_latitude'],'shop_longtude':k['shop_longtude'],'shop_description':k['shop_description'],'shop_operations_status':k['shop_operations_status'],'date_created':k['date_created'],'national_id':current_user.national_id},key)
            
            return 'product not available or shop not operational'
        
    except Exception:
        
        return 'error'
    
@app.put('/Add_subract_quantity/',tags = ['Quantity'])
async def Add_subtract_quantity(unique_name : str = Form(...),quantity : int = Form(...),method : str = Form(...),current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            for k in goods.fetch({'national_id':current_user.national_id,'shop_operations_status':'operational'})._items:
                if k['unique_name'] == unique_name:
                    key = k['key']
                    og_quantity = k['quantity']
                    
                    if method == 'add_stock':
                        
                        new_quantity = og_quantity + abs(quantity)
                        
                        transactions_history.put({'seller':current_user.full_name,'national_id':current_user.national_id,'product_unique_name':unique_name,'product_name':k['name'],'price':k['price'],'quantity':new_quantity,'shop_name':k['shop_name'],'transaction_type':'add_stock','by':abs(quantity),'transaction_date':str(datetime.today())})
                    
                        return goods.put({'seller':current_user.full_name,'unique_name':unique_name,'name':k['name'],'description':k['description'],'price':k['price'],'quantity':new_quantity,'method_of_payment':k['method_of_payment'],'shop_name':k['shop_name'],'shop_location':k['shop_location'],'shop_latitude':k['shop_latitude'],'shop_longtude':k['shop_longtude'],'shop_description':k['shop_description'],'shop_operations_status':k['shop_operations_status'],'date_created':k['date_created'],'national_id':current_user.national_id},key)
                    
                    elif method == 'physical_sale':
                        
                        new_quantity = og_quantity - abs(quantity)
                        
                        if new_quantity >= 0:
                            
                            transactions_history.put({'seller':current_user.full_name,'national_id':current_user.national_id,'product_unique_name':unique_name,'product_name':k['name'],'price':k['price'],'quantity':new_quantity,'shop_name':k['shop_name'],'transaction_type':'physical_sale','by':abs(quantity),'transaction_date':str(datetime.today())})
                            
                            return goods.put({'seller':current_user.full_name,'unique_name':unique_name,'name':k['name'],'description':k['description'],'price':k['price'],'quantity':new_quantity,'method_of_payment':k['method_of_payment'],'shop_name':k['shop_name'],'shop_location':k['shop_location'],'shop_latitude':k['shop_latitude'],'shop_longtude':k['shop_longtude'],'shop_description':k['shop_description'],'shop_operations_status':k['shop_operations_status'],'date_created':k['date_created'],'national_id':current_user.national_id},key)
                           
                        return 'quantity cannot be negative'
                    
                    elif method == 'expiration/damage':
                        
                        new_quantity = og_quantity - abs(quantity)
                        
                        if new_quantity >= 0:
                            
                            transactions_history.put({'seller':current_user.full_name,'national_id':current_user.national_id,'product_unique_name':unique_name,'product_name':k['name'],'price':k['price'],'quantity':new_quantity,'shop_name':k['shop_name'],'transaction_type':'expiration/damage','by':abs(quantity),'transaction_date':str(datetime.today())})
                            
                            return goods.put({'seller':current_user.full_name,'unique_name':unique_name,'name':k['name'],'description':k['description'],'price':k['price'],'quantity':new_quantity,'method_of_payment':k['method_of_payment'],'shop_name':k['shop_name'],'shop_location':k['shop_location'],'shop_latitude':k['shop_latitude'],'shop_longtude':k['shop_longtude'],'shop_description':k['shop_description'],'shop_operations_status':k['shop_operations_status'],'date_created':k['date_created'],'national_id':current_user.national_id},key)
                           
                        return 'quantity cannot be negative'
                    
                    return 'method not available'
                                       
            return 'product not available or shop not operational'
                    
        
    except Exception:
        
        return 'error'
    
@app.get('/Transactions_history',tags = ['History'])
async def Transactions_history_def(current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            
            return transactions_history.fetch({'national_id':current_user.national_id})._items
        
        return 'verify your account'
        
    except Exception:
        
        return 'error'
    

@app.get('/Price_history',tags = ['History'])
async def Price_history_def(current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            
            return price_history.fetch({'national_id':current_user.national_id})._items
        
        return 'verify your account'
        
    except Exception:
        
        return 'error'
    

@app.get('/Shop_open_history',tags = ['History'])
async def Shop_open_history_def(current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            
            return shops_open.fetch({'national_id':current_user.national_id})._items
        
        return 'verify your account'
        
    except Exception:
        
        return 'error'
    
@app.get('/Shop_operations_history',tags = ['History'])
async def Shop_operations_history_def(current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            
            return shops_operations.fetch({'national_id':current_user.national_id})._items
        
        return 'verify your account'
        
    except Exception:
        
        return 'error'
    
        
@app.get('/Shops_info_all',tags = ['Shop details'])
async def Shops_info_all(current_user: User = Depends(get_current_user)):
    
    try:
        
        if current_user.account_status == 'active':
            
            shops_list = []
            
            for i in  shops.fetch({'national_id':current_user.national_id})._items:
                
                goods_list = []
                
                for k in goods.fetch({'national_id':current_user.national_id,'shop_name':i['shop_name']})._items:
                    
                    transactions_history_list = transactions_history.fetch({'national_id':current_user.national_id,'product_unique_name':k['unique_name']})._items
                    price_history_list = price_history.fetch({'national_id':current_user.national_id,'product_unique_name':k['unique_name']})._items
                    
                    product_dict = {'product':k,'transactions_history':transactions_history_list,'price_history':price_history_list}
                    
                    goods_list.append(product_dict)
                    
                shops_open_list = shops_open.fetch({'national_id':current_user.national_id,'shop_name':i['shop_name']})._items        
                shops_operations_list = shops_operations.fetch({'national_id':current_user.national_id,'shop_name':i['shop_name']})._items
                   
                shop_dict = {'Shop':i,'Goods':goods_list,'Open_history':shops_open_list,'Operations_history':shops_operations_list}
                
                shops_list.append(shop_dict)
                
            return shops_list
 
        
    except Exception:
        
        return 'error'


if __name__ == '__main__':
    uvicorn.run('app:app',reload = True)
    
