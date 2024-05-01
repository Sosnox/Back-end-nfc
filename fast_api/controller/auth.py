from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form ,Path, APIRouter
from fastapi.security import OAuth2PasswordBearer
import asyncpg
import os
from service.auth import AuthService
from datetime import timedelta, datetime
import mysql.connector
from pydantic import BaseModel
from enum import Enum
from typing import Optional
import shutil

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

router = APIRouter(
    prefix="/auth",
    tags=["Authen"],
)

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

@router.post("/reg")
async def register(
    username:str=Form(...),
    password:str=Form(...),
    first_name:str=Form(...),
    last_name:str=Form(...),
    role:str=Form(...)
    ):
    connection = mysql.connector.connect(
            host="mysqldb", user="xenon", password="skizztv191", database="db-nfc-game"
        )
    conn = connection.cursor()

    conn.execute(
        '''
        INSERT INTO User(username, password, first_name, last_name, role) VALUES(%s ,%s ,%s ,%s ,%s);
        '''
        ,(username, AuthService.hash_password(password), first_name, last_name, role)
    )

    connection.commit()
    connection.close()

    return True

@router.post("/login")
async def login(
    username:str=Form(...),
    password:str=Form(...)):
    connection = mysql.connector.connect(
            host="mysqldb", user="xenon", password="skizztv191", database="db-nfc-game"
        )
    conn = connection.cursor()

    conn.execute(
        '''
        SELECT * FROM User Where username = %s;
        '''
        ,(username,)
    )

    user = conn.fetchall()[0]
    if AuthService.hash_password(password) == user[2]:
        return {
            "token":AuthService.create_token(str(user[0]), timedelta(minutes=59),user[5]),
            "exp":"59m",
            "role":user[5]
            }
    else:
        return "wrong pass"

    

