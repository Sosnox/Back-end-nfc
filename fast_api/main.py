import shutil
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form ,Path
import mysql.connector
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from enum import Enum
from typing import Optional
import os
import uuid  # ใช้สำหรับสร้างชื่อไฟล์ที่ไม่ซ้ำกัน

app = FastAPI()

if not os.path.exists("./uploaded_images"):
    os.makedirs("./uploaded_images")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # อนุญาตให้ทุก origins เข้าถึง
    allow_credentials=True,  # อนุญาตให้ใช้ credentials
    allow_methods=["*"],  # อนุญาตให้ใช้ทุก HTTP methods
    allow_headers=["*"],  # อนุญาตให้ใช้ทุก headers
)

app.mount(
    "/uploaded_images", StaticFiles(directory="./uploaded_images"), name="uploaded_images")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host="mysqldb", user="xenon", password="l3lazker", database="db-nfc-game"
        )
        return connection
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error connecting to MySQL database: {e}"
        )


def insert_report(
    name_report: str, contact: str, detail_report: str, rating: int, checktypes: str
):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        query = "INSERT INTO Report (name_report, contact, detail_report, rating, checktypes) VALUES (%s, %s, %s, %s, %s)"
        data = (name_report, contact, detail_report, rating, checktypes)
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


def get_report_data():
    connection = connect_to_mysql()
    cursor = connection.cursor(dictionary=True)
    try:
        query = "SELECT * FROM Report"
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching data from MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()


@app.get("/get_all_feedback/")
async def get_report():
    try:
        report_data = get_report_data()
        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")

@app.get("/get_feedback_by_id/")
async def get_report(id: str):
    try:
        report_data = get_report_data()
        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


@app.post("/post_feedback/")
async def insert_feedback(feedback_data: FeedbackData):
    print(feedback_data)
    try:
        name_report = feedback_data.name_report
        contact = feedback_data.contact
        detail_report = feedback_data.detail_report
        rating = feedback_data.rating
        checktypes = feedback_data.checktypes

        return insert_report(name_report, contact, detail_report, rating, checktypes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


def insert_card_data(
    title_card: str,
    detail_card: str,
    tick_card: str,
    path_image_card: str,
    count_scan_card: int,
    id_boardgame: int,
):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        query = "INSERT INTO Card (title_card, detail_card, path_image_card, tick_card, count_scan_card) VALUES (%s, %s, %s, %s, %s)"
        data = (title_card, detail_card, path_image_card, tick_card, count_scan_card)
        cursor.execute(query, data)
        connection.commit()

        id_card = cursor.lastrowid  # รับค่า id ของข้อมูลที่เพิ่มล่าสุด

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


@app.post("/post_card/")
async def post_card(
    title_card: str = Form(...),
    detail_card: str = Form(...),
    tick_card: str = Form(...),
    count_scan_card: int = Form(...),
    id_boardgame: int = Form(...),
    file: UploadFile = File(...),
):
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
            count_scan_card,
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
    count_scan_boardgame: int,
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
            count_scan_boardgame,
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


@app.post("/post_boardgame/")
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
    count_scan_boardgame: int = Form(...),
):
    try:
        uid_filename = uuid.uuid4()
        file_extension = file.filename.split(".")[-1]  # img.png/jpg
        file_location_boardgame = f"./uploaded_images/{uid_filename}.{file_extension}"
        filename = f"{uid_filename}.{file_extension}"

        with open(file_location_boardgame, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

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
            count_scan_boardgame,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


@app.get("/get_all_boardgame/")
async def get_report():
    try:
        boardgame_data = get_boardgame_data()
        return boardgame_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


def get_boardgame_data():
    connection = connect_to_mysql()
    cursor = connection.cursor(dictionary=True)
    try:
        query = "SELECT * FROM BoardGame"
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching data from MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()


@app.get("/get_all_card_by_id_boardgame/")
async def get_card_by_id_boardgame(id_boardgame: int):
    try:
        card_data = get_card_data_by_id_boardgame_data(id_boardgame)
        if not card_data:
            return "No card data found for the given board game ID."
        return card_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


def get_card_data_by_id_boardgame_data(id_boardgame: int):
    connection = connect_to_mysql()
    cursor = connection.cursor(dictionary=True)
    try:
        query = "SELECT * FROM Card INNER JOIN Connect_BoardGame_Card ON Card.id_card = Connect_BoardGame_Card.id_card WHERE Connect_BoardGame_Card.id_boardgame = %s"
        data = (id_boardgame,)
        cursor.execute(query, data)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching data from MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()


@app.get("/get_boardgame_by_id_boardgame/")
async def get_boardgame_by_id_boardgame(id_boardgame: int):
    try:
        boardgame_data = get_boardgame_data_by_id_boardgame_data(id_boardgame)
        if not boardgame_data:
            return "No card data found for the given board game ID."
        return boardgame_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


def get_boardgame_data_by_id_boardgame_data(id_boardgame: int):
    connection = connect_to_mysql()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True here
    try:
        query = "SELECT * FROM BoardGame WHERE id_boardgame = %s"
        data = (id_boardgame,)
        cursor.execute(query, data)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching data from MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()


@app.get("/get_card_by_name_boardgame/")
async def get_Card_by_name_boardgame(name_boardgame: str):
    try:
        boardgame_data = get_Card_by_name_boardgame(name_boardgame)
        if not boardgame_data:
            return "No card data found for the given board game ID."
        return boardgame_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


def get_Card_by_name_boardgame(name_boardgame: str):
    connection = connect_to_mysql()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True here
    try:
        query = "SELECT * FROM Card WHERE title_card = %s"
        data = (name_boardgame,)
        cursor.execute(query, data)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching data from MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

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

@app.patch("/update_card/{id_card}")
async def update_card(
    id_card: int = Path(..., title="The ID of the card to update"),
    title_card: Optional[str] = Form(None),
    detail_card: Optional[str] = Form(None),
    tick_card: Optional[str] = Form(None),
    count_scan_card: Optional[int] = Form(None),
    Image_file: UploadFile = File(None),
):
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


@app.patch("/update_boardgame/{id_boardgame}")
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
):
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


# def insert_user_admin(username: str, password: str, first_name: str, last_name: str, role: UserRole):
#     connection = connect_to_mysql()
#     cursor = connection.cursor()
#     try:
        #   if role not in UserRole.__members__.values():
        #         raise ValueError("Invalid role. Choose 'super_admin' or 'admin'.")
#         query = "INSERT INTO User (username, password, first_name, last_name, role) VALUES (%s, %s, %s, %s, %s)"
#         data = (username, password, first_name, last_name, role)
#         cursor.execute(query, data)
#         connection.commit()
#         return {"message": "Data inserted successfully"}
#     except Exception as e:
#         connection.rollback()
#         raise HTTPException(
#             status_code=500, detail=f"Error inserting data into MySQL database: {e}"
#         )
#     finally:
#         cursor.close()
#         connection.close()


# @app.post("/post_user_admin/")
# async def post_user_admin(username: str, password: str, first_name: str, last_name: str, role: str):
#     try:
#         return insert_user_admin(username, password, first_name, last_name, role)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


def insert_user_admin(username: str, hashed_password: str, first_name: str, last_name: str, role: UserRole):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        # Check if the role is valid
        if role not in UserRole.__members__.values():
            raise ValueError("Invalid role. Choose 'super_admin' or 'admin'.")
        query = "INSERT INTO User (username, password, first_name, last_name, role) VALUES (%s, %s, %s, %s, %s)"
        data = (username, hashed_password, first_name, last_name, role)
        cursor.execute(query, data)
        connection.commit()
        return {"message": "Data inserted successfully", "id_user": cursor.lastrowid}
    except mysql.connector.Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error inserting data into MySQL database: {e}"
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=400, detail=str(ve)
        )
    finally:
        cursor.close()
        connection.close()

@app.post("/post_user_admin/")
async def post_user_admin(username: str, password: str, first_name: str, last_name: str, role: UserRole):
    hashed_password = pwd_context.hash(password)  # Hashing the password
    try:
        return insert_user_admin(username, hashed_password, first_name, last_name, role)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


def delete_user_admin(username: str):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        query = "DELETE FROM User WHERE username = %s"
        data = (username,)
        cursor.execute(query, data)
        connection.commit()
        if cursor.rowcount == 0:
            return {"message": "No user found with that username."}
        return {"message": "User deleted successfully"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting user from MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@app.delete("/delete_user_admin/{username}")
async def delete_user_admin_endpoint(username: str):
    try:
        return delete_user_admin(username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")

def get_user_admin(username: str):
    connection = connect_to_mysql()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True to return data as a dict
    try:
        query = "SELECT * FROM User WHERE username = %s"
        data = (username,)
        cursor.execute(query, data)
        result = cursor.fetchone()  # Fetch only one record
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

@app.get("/get_user_admin/{username}", response_model=User)
async def get_user_admin_endpoint(username: str):
    try:
        user_info = get_user_admin(username)
        if "message" in user_info:
            raise HTTPException(status_code=404, detail=user_info["message"])
        return user_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


def delete_card(id_card: str):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        query = "DELETE FROM Card WHERE id_card = %s"
        data = (id_card,)
        cursor.execute(query, data)
        connection.commit()
        if cursor.rowcount == 0:
            return {"message": "No user found with that id_card."}
        return {"message": "User deleted successfully"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting user from MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@app.delete("/delete_card/{id_card}")
async def delete_card_endpoint(id_card: str):
    try:
        return delete_card(id_card)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


def delete_boardgame(id_boardgame: str):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        query = "DELETE FROM BoardGame WHERE id_boardgame = %s"
        data = (id_boardgame,)
        cursor.execute(query, data)
        connection.commit()
        if cursor.rowcount == 0:
            return {"message": "No user found with that id_boardgame."}
        return {"message": "User deleted successfully"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error deleting user from MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@app.delete("/delete_card/{id_boardgame}")
async def delete_boardgame_endpoint(id_boardgame: str):
    try:
        return delete_boardgame(id_boardgame)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")