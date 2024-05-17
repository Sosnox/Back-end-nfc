from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form ,Path, APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
import asyncpg
import os
from service.auth import AuthService
from datetime import timedelta, datetime
import mysql.connector
from pydantic import BaseModel
from enum import Enum
from typing import Optional
import uuid
import shutil

router = APIRouter(
    prefix="/superadmin",
    tags=["Super Admin"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class FeedbackData(BaseModel):
    name_report: str
    contact: str
    detail_report: str
    rating: int
    checktypes: str

class UserRole(str, Enum):
    super_admin = 'super_admin'
    admin = 'admin'

class BoardGameData(BaseModel):
    title_game: str
    detail_game: str
    path_image_boardgame: str
    path_youtube : str
    player_recommend_start: int
    player_recommend_end: int
    age_recommend: int
    time_playing: int
    count_scan_boardgame: int

class User(BaseModel):
    username: str
    password: str  # Consider omitting sensitive data like passwords in actual response
    first_name: str
    last_name: str
    role: str

class CardData(BaseModel):
    title_card: str
    detail_card: str
    path_image_card: str
    count_scan_card: int
    id_boardgame: int

class UserRole(str, Enum):
    super_admin = "super_admin"
    admin = "admin"

def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host="mysqldb", user="xenon", password="skizztv191", database="db-nfc-game"
        )
        return connection
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error connecting to MySQL database: {e}"
        )

def get_user_admin():
    connection = connect_to_mysql()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True to return data as a dict
    try:
        query = "SELECT * FROM User"
        cursor.execute(query)
        result = cursor.fetchall()  # Fetch only one record
        if result is None:
            return {"message": "No user found with that username."}
        return result
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving user from MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@router.get("/get_user_admin/")
async def get_user_admin_endpoint(token:str = Depends(oauth2_scheme)):
    AuthService.isSuperAdmin(token)
    try:
        user_info = get_user_admin()
        if "message" in user_info:
            raise HTTPException(status_code=404, detail=user_info["message"])
        return user_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")

def insert_user_admin(username: str, password: str, first_name: str, last_name: str, role: UserRole):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        if role not in UserRole.__members__.values():
            raise ValueError("Invalid role. Choose 'super_admin' or 'admin'.")
        query = "INSERT INTO User (username, password, first_name, last_name, role) VALUES (%s, %s, %s, %s, %s)"
        data = (username, AuthService.hash_password(password), first_name, last_name, role)
        cursor.execute(query, data)
        connection.commit()
        return {"message": "Data inserted successfully"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error inserting data into MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@router.post("/post_user_admin/")
async def post_user_admin(username:str=Form(...), password:str=Form(...), first_name:str=Form(...), last_name:str=Form(...), role: UserRole = Form(...),token:str = Depends(oauth2_scheme)):
    AuthService.isSuperAdmin(token)
    try:
        return insert_user_admin(username, password, first_name, last_name, role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")

@router.delete("/delete_admin/{admin_id}")
async def get_user_admin_endpoint(admin_id:int,token:str = Depends(oauth2_scheme)):
    AuthService.isSuperAdmin(token)
    connection = connect_to_mysql()
    cursor = connection.cursor(dictionary=True)

    try:
        query = "DELETE FROM User WHERE id_user = %s"
        data = (admin_id,)
        cursor.execute(query, data)
        connection.commit()
        return {"status": "success", "message": "User deleted successfully"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error inserting data into MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@router.patch("/forcePass_admin")
async def get_user_admin_endpoint(id:int=Form(...),password:str=Form(...),token:str = Depends(oauth2_scheme)):
    AuthService.isSuperAdmin(token)
    connection = connect_to_mysql()
    cursor = connection.cursor(dictionary=True)

    try:
        query = "UPDATE User SET password = %s WHERE id_user = %s"
        data = (AuthService.hash_password(password), str(id))
        cursor.execute(query, data)
        connection.commit()
        return {"status": "success", "message": "Password updated successfully"} 
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error inserting data into MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()