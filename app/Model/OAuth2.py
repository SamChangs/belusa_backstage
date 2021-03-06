import jwt
from fastapi import Depends, HTTPException, status
from Entity.meta import *

JWT_SECRET = 'myjwtsecret'


class AuthUser():
    def __init__(self, u_Pydantic,ui_Pydantic):
        self.User_Pydantic = u_Pydantic
        self.UserIn_Pydantic = ui_Pydantic
      
    async def authenticate_user(self,username: str, password: str):
        user = await User.get(account=username) #取得 account=username 的 user 物件
        if not user:
            return False 
        if not user.verify_password(password):
            return False
        return user 

    async def generate_token(self, form_data):
        user =  await  self.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail='Invalid username or password'
            )

        user_obj =  await  self.User_Pydantic.from_tortoise_orm(user)

        user_dict = user_obj.dict()
        
        user_dict.pop("password_hash",None)

    
        token = jwt.encode(user_dict, JWT_SECRET)

        return {'access_token' : token, 'token_type' : 'bearer'}
  
    async def get_current_user(self,token):  
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user = await User.get(id=payload.get('id'))
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail='Invalid username or password'
            )

        return await self.User_Pydantic.from_tortoise_orm(user)

