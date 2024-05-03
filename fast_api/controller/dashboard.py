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
from datetime import datetime

router = APIRouter(
    prefix="/dash",
    tags=["Dashboard"],
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

@router.get('/circleGraph')
def countScanAscend():
    connection = connect_to_mysql()
    conn = connection.cursor(dictionary=True)
    conn.execute('SELECT id_boardgame, title_game, count_scan_boardgame FROM BoardGame;')
    result = conn.fetchall()
    return sorted(result, key=lambda x: x['count_scan_boardgame'], reverse=True)

@router.get('/decendReport')
def reportAscend():
    connection = connect_to_mysql()
    conn = connection.cursor(dictionary=True)
    conn.execute('SELECT id_report, detail_report, date_report FROM Report;')
    result = conn.fetchall()
    return sorted(result, key=lambda x: x['date_report'], reverse=True)

@router.get('/countCardScan')
def countCardScan():
    connection = connect_to_mysql()
    conn = connection.cursor(dictionary=True)
    conn.execute('SELECT id_card, title_card, count_scan_card FROM Card;')
    result = conn.fetchall()
    return sorted(result, key=lambda x: x['count_scan_card'], reverse=True)

# @router.get('/decendReportByDate/{date}')
# def decendReportByDate(date:datetime):
#     connection = connect_to_mysql()
#     conn = connection.cursor(dictionary=True)
#     conn.execute('SELECT id_report, detail_report, date_report FROM Report WHERE date_report = %s;',(date,))
#     result = conn.fetchall()
#     return sorted(result, key=lambda x: x['date_report'], reverse=True)

@router.get('/decendReportByDate/{date}')
def decendReportByDate(date: datetime):
    connection = connect_to_mysql()
    conn = connection.cursor(dictionary=True)
    
    # Convert datetime object to string in format 'YYYY-MM-DD'
    date_str = date.strftime('%Y-%m-%d')
    
    # Execute query to select reports on the given date
    conn.execute('SELECT id_report, detail_report, date_report FROM Report WHERE date(date_report) = %s;', (date_str,))
    result = conn.fetchall()
    
    # Ensure all dates are converted to datetime objects if they are not already
    for r in result:
        if isinstance(r['date_report'], str):
            r['date_report'] = datetime.strptime(r['date_report'], '%Y-%m-%d %H:%M:%S')
    
    # Sort results by date in descending order without considering time
    result = sorted(result, key=lambda x: x['date_report'].strftime('%d/%m/%y'), reverse=True)
    return result
