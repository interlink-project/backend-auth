from datetime import datetime
from turtle import up
from app.database import collection
from app.model import UserSchema
from fastapi.encoders import jsonable_encoder

async def get(id: str):
    return await collection.find_one({"_id": id})

async def get_all():
    return await collection.find().to_list(1000)
    
async def create(user_info: dict):
    user = UserSchema(**user_info)
    user = jsonable_encoder(user)
    db_asset = await collection.insert_one(user)
    return await get(db_asset.inserted_id)

async def update(id: str, data):
    await collection.update_one( { "_id": id }, { "$set": data })
    return await get(id)

async def delete(id: str):
    return await collection.delete_one({"_id": id})

async def login(user_info: dict):
    user_id = user_info["sub"]
    user_info = await get(user_id)

    user_info["_id"] = user_id
    user_info["last_login"] = datetime.now()
    if not user_info:
        print("Creating user")
        return await create(user_info)
    print("Updating user")
    return await update(user_id, user_info)

async def get_or_create(user_info: dict):
    user_id = user_info["sub"]
    user_info = await get(user_id)

    user_info["_id"] = user_id
    user_info["last_login"] = datetime.now()
    if not user_info:
        print("Creating user")
        return await create(user_info)
    return user_info