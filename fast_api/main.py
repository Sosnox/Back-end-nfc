import shutil
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
import mysql.connector
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
    "/uploaded_images", StaticFiles(directory="./uploaded_images"), name="uploaded_images"
)  # api/static/filename.jpg


class FeedbackData(BaseModel):
    name_report: str
    contact: str
    detail_report: str
    rating: int
    checktypes: str


class BoardGameData(BaseModel):
    title_game: str
    detail_game: str
    path_image_boardgame: str
    player_recommend_start: int
    player_recommend_end: int
    age_recommend: int
    time_playing: int
    count_scan_boardgame: int


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