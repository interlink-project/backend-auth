from datetime import datetime
from turtle import up
from app.model import UserSchema
from fastapi.encoders import jsonable_encoder
from app.database import AsyncIOMotorCollection
from pydantic import BaseModel, Field


class User(BaseModel):
    sub: str
    zoneinfo: str
    preferred_username: str
    email: str
    locale: str
    given_name: str
    family_name: str
    picture: str
    last_login: datetime


async def get(collection: AsyncIOMotorCollection, id: str):
    return await collection.find_one({
        '$or': [
            {'_id': id},
            {'email': id}
        ]})


async def get_by_email(collection: AsyncIOMotorCollection, email: str):
    return await collection.find_one({"email": email})


async def get_all(collection: AsyncIOMotorCollection):
    return await collection.find().to_list(1000)


async def create(collection: AsyncIOMotorCollection, user_info: dict):
    user = UserSchema(**user_info)
    user = jsonable_encoder(user)
    db_asset = await collection.insert_one(user)
    return await get(collection, db_asset.inserted_id)


async def update(collection: AsyncIOMotorCollection, id: str, data):
    await collection.update_one({"_id": id}, {"$set": data})
    return await get(collection, id)


async def delete(collection: AsyncIOMotorCollection, id: str):
    return await collection.delete_one({"_id": id})


async def login(collection: AsyncIOMotorCollection, user_info: dict):
    user_id = user_info["sub"]
    db_user_info = await get(collection, user_id)

    user_info["_id"] = user_id
    user_info["last_login"] = datetime.now()
    if not db_user_info:
        print("Creating user")
        return await create(collection, user_info)
    print("Updating user")
    return await update(collection, user_id, user_info)


async def get_or_create(collection: AsyncIOMotorCollection, user_info: dict):
    user_id = user_info["sub"]
    db_user_info = await get(collection, user_id)

    if not db_user_info:
        user_info["_id"] = user_id
        user_info["last_login"] = datetime.now()
        print("Creating user")
        return await create(collection, user_info)
    email = user_info["email"]
    print(f"Returning db user for {email}")
    return {**user_info, **db_user_info}
