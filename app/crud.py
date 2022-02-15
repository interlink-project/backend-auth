import mimetypes
import requests
from fastapi.encoders import jsonable_encoder

from app.database import AsyncIOMotorCollection
from app.model import UserSchema


async def get(collection: AsyncIOMotorCollection, id: str):
    return await collection.find_one({
        '$or': [
            {'_id': id},
            {'email': id},
            {'sub': id}
        ]})

async def get_all(collection: AsyncIOMotorCollection):
    return await collection.find().to_list(1000)


async def create(collection: AsyncIOMotorCollection, user_info: dict):
    print("CREATING FROM ", user_info)
    user_id = user_info["sub"]
    user_info["_id"] = user_id
    if "picture" in user_info:
        response = requests.get(user_info["picture"])
        content_type = response.headers['content-type']
        extension = mimetypes.guess_extension(content_type)
        URL = f"/static/{user_id}{extension}"
        with open("/app" + URL, 'wb') as handler:
            handler.write(response.content)
        user_info["picture"] = URL
    if "given_name" in user_info and "family_name" in user_info:
        user_info["full_name"] = user_info["given_name"] + " " + user_info["family_name"]

    user = UserSchema(**user_info)
    user = jsonable_encoder(user)
    user["_id"] = user_id
    db_asset = await collection.insert_one(user)
    return await get(collection, db_asset.inserted_id)


async def update(collection: AsyncIOMotorCollection, id: str, user_info: dict):
    user = UserSchema(**user_info)
    user = jsonable_encoder(user)
    await collection.update_one({"_id": id}, {"$set": user})
    return await get(collection, id)


async def delete(collection: AsyncIOMotorCollection, id: str):
    return await collection.delete_one({"_id": id})


async def login(collection: AsyncIOMotorCollection, user_info: dict):
    user_id = user_info["sub"]
    db_user_info = await get(collection, user_id)
    if not db_user_info:
        print("Creating user from login")
        return await create(collection, user_info)

    print("Updating user")
    return await update(collection, user_id, user_info)


async def get_or_create(collection: AsyncIOMotorCollection, user_info: dict):
    user_id = user_info["sub"]
    db_user_info = await get(collection, user_id)
    if not db_user_info:
        print("Creating user from get_or_create")
        db_user_info = await create(collection=collection, user_info=user_info)
    email = user_info["email"]
    print(f"Returning db user for {email}")
    return { **user_info, **db_user_info}
