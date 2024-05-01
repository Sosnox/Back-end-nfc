
import shutil
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form ,Path
import mysql.connector
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from passlib.context import CryptContext
from enum import Enum
from typing import Optional
import os
import uuid


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

from controller.auth import router as auth_router
app.include_router(auth_router)
from controller.admin import router as admin_router
app.include_router(admin_router)
from controller.superadmin import router as superadmin_router
app.include_router(superadmin_router)

app.mount(
    "/uploaded_images", StaticFiles(directory="./uploaded_images"), name="uploaded_images")

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

def update_count_view(id_boardgame: int):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        query = "UPDATE BoardGame SET count_scan_boardgame = count_scan_boardgame + 1 WHERE id_boardgame = %s"
        cursor.execute(query, (id_boardgame,))
        connection.commit()
        print("Count updated successfully")
        return {"message": f"Updating count for board game with ID_Boardgame {id_boardgame}"}
    except Exception as e:
        print(f"Error updating data in MySQL database: {e}")
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating data in MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

def insert_report(
    name_report: str, detail_report: str, rating: int, checktypes: str
):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        query = "INSERT INTO Report (name_report, detail_report, rating, checktypes) VALUES (%s, %s, %s, %s)"
        data = (name_report, detail_report, rating, checktypes)
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
        detail_report = feedback_data.detail_report
        rating = feedback_data.rating
        checktypes = feedback_data.checktypes

        return insert_report(name_report, detail_report, rating, checktypes)
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
            return []
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
            return []
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

def insert_user_admin(username: str, password: str, first_name: str, last_name: str, role: UserRole):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        if role not in UserRole.__members__.values():
            raise ValueError("Invalid role. Choose 'super_admin' or 'admin'.")
        query = "INSERT INTO User (username, password, first_name, last_name, role) VALUES (%s, %s, %s, %s, %s)"
        data = (username, password, first_name, last_name, role)
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


# @app.post("/post_user_admin/")
# async def post_user_admin(username: str, password: str, first_name: str, last_name: str, role: UserRole):
#     try:
#         return insert_user_admin(username, password, first_name, last_name, role)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


# def insert_user_admin(username: str, hashed_password: str, first_name: str, last_name: str, role: UserRole):
#     connection = connect_to_mysql()
#     cursor = connection.cursor()
#     try:
#         # Check if the role is valid
#         if role not in UserRole.__members__.values():
#             raise ValueError("Invalid role. Choose 'super_admin' or 'admin'.")
#         query = "INSERT INTO User (username, password, first_name, last_name, role) VALUES (%s, %s, %s, %s, %s)"
#         data = (username, hashed_password, first_name, last_name, role)
#         cursor.execute(query, data)
#         connection.commit()
#         return {"message": "Data inserted successfully", "id_user": cursor.lastrowid}
#     except mysql.connector.Error as e:
#         connection.rollback()
#         raise HTTPException(
#             status_code=500, detail=f"Error inserting data into MySQL database: {e}"
#         )
#     except ValueError as ve:
#         raise HTTPException(
#             status_code=400, detail=str(ve)
#         )
#     finally:
#         cursor.close()
#         connection.close()

# @app.post("/post_user_admin/")
# async def post_user_admin(username: str, password: str, first_name: str, last_name: str, role: UserRole):
#     hashed_password = pwd_context.hash(password)  # Hashing the password
#     try:
#         return insert_user_admin(username, hashed_password, first_name, last_name, role)
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing request: {e}")


# def delete_user_admin(username: str):
#     connection = connect_to_mysql()
#     cursor = connection.cursor()
#     try:
#         query = "DELETE FROM User WHERE username = %s"
#         data = (username,)
#         cursor.execute(query, data)
#         connection.commit()
#         if cursor.rowcount == 0:
#             return {"message": "No user found with that username."}
#         return {"message": "User deleted successfully"}
#     except Exception as e:
#         connection.rollback()
#         raise HTTPException(
#             status_code=500, detail=f"Error deleting user from MySQL database: {e}"
#         )
#     finally:
#         cursor.close()
#         connection.close()

# @app.delete("/delete_user_admin/{username}")
# async def delete_user_admin_endpoint(username: str):
#     try:
#         return delete_user_admin(username)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing request: {e}")



@app.patch("/update_count_view/{id_boardgame}")
async def update_count_views(id_boardgame: int):
    try:
        print(f"Received request to update count for ID {id_boardgame}")
        return update_count_view(id_boardgame)
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")

def update_count_view_card(title_card: str):
    connection = connect_to_mysql()
    cursor = connection.cursor()
    try:
        query = "UPDATE Card SET count_scan_card = count_scan_card + 1 WHERE title_card = %s"
        cursor.execute(query, (title_card,))
        connection.commit()
        print("Count updated successfully")
        return {"message": f"Updating count for board game with ID_Card {title_card}"}
    except Exception as e:
        print(f"Error updating data in MySQL database: {e}")
        connection.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error updating data in MySQL database: {e}"
        )
    finally:
        cursor.close()
        connection.close()

@app.patch("/update_count_view_card/{title_card}")
async def update_count_views_card(title_card: str):
    try:
        print(f"Received request to update count for ID {title_card}")
        return update_count_view_card(title_card)
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")