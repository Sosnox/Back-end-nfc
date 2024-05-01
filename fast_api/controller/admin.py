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
    prefix="/admin",
    tags=["Admin"],
)

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

def insert_card_data(
    title_card: str,
    detail_card: str,
    tick_card: str,
    path_image_card: str,
    id_boardgame: int,
):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        query = "INSERT INTO Card (title_card, detail_card, path_image_card, tick_card, count_scan_card) VALUES (%s, %s, %s, %s, %s)"
        data = (title_card, detail_card, path_image_card, tick_card, 0)
        cursor.execute(query, data)
        connection.commit()

        id_card = cursor.lastrowid

        query = (
            "INSERT INTO Connect_BoardGame_Card (id_boardgame, id_card) VALUES (%s, %s)"
        )
        data = (id_boardgame, id_card)
        cursor.execute(query, data)
        connection.commit()

        return {"message": "Data inserted successfully"}
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error inserting data into MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@router.post("/post_card/")
async def post_card(
    title_card: str = Form(...),
    detail_card: str = Form(...),
    tick_card: str = Form(...),
    id_boardgame: int = Form(...),
    file: UploadFile = File(...),
    # token:str = Depends(oauth2_scheme)
):
    # AuthService.isAdmin(token)
    try:
        uid_filename = uuid.uuid4()
        file_extension = file.filename.split(".")[-1]  # img.png/jpg
        file_location_card = f"./uploaded_images/{uid_filename}.{file_extension}"
        filename = f"{uid_filename}.{file_extension}"

        with open(file_location_card, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)


        response = insert_card_data(
            title_card,
            detail_card,
            tick_card,
            filename,
            id_boardgame,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


def insert_boardgame(
    title_game: str,
    detail_game: str,
    path_image_boardgame: str,
    path_youtube: str,
    player_recommend_start: int,
    player_recommend_end: int,
    recommend: bool,
    age_recommend: int,
    time_playing: int,
    type_game: str,
):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        query = "INSERT INTO BoardGame (title_game, detail_game, path_image_boardgame, path_youtube, player_recommend_start, player_recommend_end, recommend, age_recommend, time_playing, type_game, count_scan_boardgame) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data = (
            title_game,
            detail_game,
            path_image_boardgame,
            path_youtube,
            player_recommend_start,
            player_recommend_end,
            recommend,
            age_recommend,
            time_playing,
            type_game,
            0,
        )
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

@router.post("/post_boardgame/")
async def post_boardgame(
    title_game: str = Form(...),
    detail_game: str = Form(...),
    file: UploadFile = File(...),
    path_youtube: str = Form(...),
    player_recommend_start: int = Form(...),
    player_recommend_end: int = Form(...),
    recommend: bool = Form(...),
    age_recommend: int = Form(...),
    time_playing: int = Form(...),
    type_game: str = Form(...),
    # token:str = Depends(oauth2_scheme)
):
    # AuthService.isAdmin(token)
    try:
        uid_filename = uuid.uuid4()
        file_extension = file.filename.split(".")[-1]  # img.png/jpg
        file_location_boardgame = f"./uploaded_images/{uid_filename}.{file_extension}"
        filename = f"{uid_filename}.{file_extension}"

        with open(file_location_boardgame, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        count_scan_boardgame = 0

        return insert_boardgame(
            title_game,
            detail_game,
            filename,
            path_youtube,
            player_recommend_start,
            player_recommend_end,
            recommend,
            age_recommend,
            time_playing,
            type_game,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")

def update_card_data(
    id_card: int,
    title_card: Optional[str] = None,
    detail_card: Optional[str] = None,
    tick_card: Optional[str] = None,
    path_image_card: Optional[str] = None,
    count_scan_card: Optional[int] = None,
):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    updates = []
    data = []

    if title_card is not None:
        updates.append("title_card = %s")
        data.append(title_card)
    if detail_card is not None:
        updates.append("detail_card = %s")
        data.append(detail_card)
    if tick_card is not None:
        updates.append("tick_card = %s")
        data.append(tick_card)
    if path_image_card is not None:
        updates.append("path_image_card = %s")
        data.append(path_image_card)
    if count_scan_card is not None:
        updates.append("count_scan_card = %s")
        data.append(count_scan_card)

    data.append(id_card)
    update_clause = ", ".join(updates)
    if updates:
        query = f"UPDATE Card SET {update_clause} WHERE id_card = %s"
        try:
            cursor.execute(query, tuple(data))
            connection.commit()
        except mysql.connector.Error as e:
            connection.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error updating data in MySQL database: {e}"
            )
        finally:
            cursor.close()
            connection.close()
        return {"message": "Card updated successfully"}
    else:
        cursor.close()
        connection.close()
        return {"message": "No updates performed"}

@router.patch("/update_card/{id_card}")
async def update_card(
    id_card: int = Path(..., title="The ID of the card to update"),
    title_card: Optional[str] = Form(None),
    detail_card: Optional[str] = Form(None),
    tick_card: Optional[str] = Form(None),
    count_scan_card: Optional[int] = Form(None),
    Image_file: UploadFile = File(None),
    # token:str = Depends(oauth2_scheme)
):
    # AuthService.isAdmin(token)
    filename = None
    if Image_file:
        uid_filename = uuid.uuid4()
        file_extension = Image_file.filename.split(".")[-1]
        file_location_card = f"./uploaded_images/{uid_filename}.{file_extension}"
        filename = f"{uid_filename}.{file_extension}"

        with open(file_location_card, "wb") as buffer:
            shutil.copyfileobj(Image_file.file, buffer)

    response = update_card_data(
        id_card,
        title_card,
        detail_card,
        tick_card,
        filename,
        count_scan_card,
    )
    return response

def update_boardgame_data(
    id_boardgame: int,
    title_game: Optional[str] = None,
    detail_game: Optional[str] = None,
    path_image_boardgame: Optional[str] = None,
    path_youtube: Optional[str] = None,
    player_recommend_start: Optional[int] = None,
    player_recommend_end: Optional[int] = None,
    recommend: Optional[bool] = None,
    age_recommend: Optional[int] = None,
    time_playing: Optional[int] = None,
    type_game: Optional[str] = None,
    count_scan_boardgame: Optional[int] = None,
):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    updates = []
    data = []

    if title_game is not None:
        updates.append("title_game = %s")
        data.append(title_game)
    if detail_game is not None:
        updates.append("detail_game = %s")
        data.append(detail_game)
    if path_image_boardgame is not None:
        updates.append("path_image_boardgame = %s")
        data.append(path_image_boardgame)
    if path_youtube is not None:
        updates.append("path_youtube = %s")
        data.append(path_youtube)
    if player_recommend_start is not None:
        updates.append("player_recommend_start = %s")
        data.append(player_recommend_start)
    if player_recommend_end is not None:
        updates.append("player_recommend_end = %s")
        data.append(player_recommend_end)
    if recommend is not None:
        updates.append("recommend = %s")
        data.append(recommend)
    if age_recommend is not None:
        updates.append("age_recommend = %s")
        data.append(age_recommend)
    if time_playing is not None:
        updates.append("time_playing = %s")
        data.append(time_playing)
    if type_game is not None:
        updates.append("type_game = %s")
        data.append(type_game)
    if count_scan_boardgame is not None:
        updates.append("count_scan_boardgame = %s")
        data.append(count_scan_boardgame)

    data.append(id_boardgame)
    update_clause = ", ".join(updates)
    if updates:
        query = f"UPDATE BoardGame SET {update_clause} WHERE id_boardgame = %s"
        try:
            cursor.execute(query, tuple(data))
            connection.commit()
        except mysql.connector.Error as e:
            connection.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error updating data in MySQL database: {e}"
            )
        finally:
            cursor.close()
            connection.close()
        return {"message": "Board game updated successfully"}
    else:
        cursor.close()
        connection.close()
        return {"message": "No updates performed"}


@router.patch("/update_boardgame/{id_boardgame}")
async def update_boardgame(
    id_boardgame: int = Path(..., title="The ID of the board game to update"),
    title_game: Optional[str] = Form(None),
    detail_game: Optional[str] = Form(None),
    path_youtube: Optional[str] = Form(None),
    player_recommend_start: Optional[int] = Form(None),
    player_recommend_end: Optional[int] = Form(None),
    recommend: Optional[bool] = Form(None),
    age_recommend: Optional[int] = Form(None),
    time_playing: Optional[int] = Form(None),
    type_game: Optional[str] = Form(None),
    count_scan_boardgame: Optional[int] = Form(None),
    Image_file: UploadFile = File(None),
    # token:str = Depends(oauth2_scheme)
):
    # AuthService.isAdmin(token)
    filename = None
    if Image_file:
        uid_filename = uuid.uuid4()
        file_extension = Image_file.filename.split(".")[-1]
        file_location_boardgame = f"./uploaded_images/{uid_filename}.{file_extension}"
        filename = f"{uid_filename}.{file_extension}"

        with open(file_location_boardgame, "wb") as buffer:
            shutil.copyfileobj(Image_file.file, buffer)

    response = update_boardgame_data(
        id_boardgame,
        title_game,
        detail_game,
        filename,
        path_youtube,
        player_recommend_start,
        player_recommend_end,
        recommend,
        age_recommend,
        time_playing,
        type_game,
        count_scan_boardgame,
    )
    return response


def delete_card(id_card: str):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        # First, retrieve the path of the image for the card to be deleted
        cursor.execute("SELECT path_image_card FROM Card WHERE id_card = %s", (id_card,))
        image_info = cursor.fetchone()

        # Check for and delete any dependencies in the Connect_BoardGame_Card table
        cursor.execute("DELETE FROM Connect_BoardGame_Card WHERE id_card = %s", (id_card,))

        # Now attempt to delete the card itself
        cursor.execute("DELETE FROM Card WHERE id_card = %s", (id_card,))
        connection.commit()

        if cursor.rowcount == 0:
            return {"message": "No card found with that id_card."}


        if image_info:  # This will be true if the fetch was successful
            image_path = os.path.join('uploaded_images', str(image_info[0]))
            os.remove(image_path)

        return {"message": "Card deleted successfully"}

    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting card from MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@router.delete("/delete_card/{id_card}")
async def delete_card_endpoint(
    id_card: str
    # ,token:str = Depends(oauth2_scheme)
):
    # AuthService.isAdmin(token)
    try:
        return delete_card(id_card)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")

# #################################################################
def delete_boardgame(id_boardgame: str):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        # Get the image path before deletion
        cursor.execute("SELECT path_image_boardgame FROM BoardGame WHERE id_boardgame = %s", (id_boardgame,))
        image_info = cursor.fetchone()

        # Delete the boardgame
        cursor.execute("DELETE FROM BoardGame WHERE id_boardgame = %s", (id_boardgame,))
        connection.commit()

        if cursor.rowcount == 0:
            return {"message": "No boardgame found with that id_boardgame."}

        # Delete the image file
        if image_info:
            image_path = os.path.join('uploaded_images', str(image_info[0]))
            os.remove(image_path)

        return {"message": "Card and associated image deleted successfully"}

    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting boardgame from MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@router.delete("/delete_boardgame/{id_boardgame}")
async def delete_boardgame_endpoint(
    id_boardgame: str
    # ,token:str = Depends(oauth2_scheme)
    ):
    # AuthService.isAdmin(token)
    try:
        return delete_boardgame(id_boardgame)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")
# #################################################################

