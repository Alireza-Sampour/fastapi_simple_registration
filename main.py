import hashlib

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from db import DB


app = FastAPI()
database = None
salt = "xNC&GQ67"

class User(BaseModel):
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    phone_number: Union[str, None] = None
    password: str


class Login(BaseModel):
    email: Union[str, None] = None
    phone_number: Union[str, None] = None
    password: str


@app.on_event("startup")
def setup():
    print(">>> Creating db tables...")
    global database
    database = DB()
    database.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255), full_name VARCHAR(255), phone_number VARCHAR(255), `password` VARCHAR(255));")
    print(">>> Done.") 


@app.post("/signup/")
def signup(user: User):
    global database
    if user.email and user.phone_number:
        return {"status": "false", "message": "You can't use both email and phone number."}
    else:
        if str(user.email or '') == '' and str(user.phone_number or '') == '':
            return {"status": "false", "message": "You must provide either email or phone number."}
        if user.email is not None:
            if database.fetch_one("SELECT * FROM users WHERE email = %s;", (user.email,)):
                return {"status": "false", "message": "Email already exists."}
        if user.phone_number is not None:
            if database.fetch_one("SELECT * FROM users WHERE phone_number = %s;", (user.phone_number,)):
                return {"status": "false", "message": "Phone number already exists."}     
    if user.full_name is None:
        return {"status": "false", "message": "You must provide full name."}
    if user.password is None:
        return {"status": "false", "message": "You must provide a password."}

    hashed_password = hashlib.md5((user.password + salt).encode()).hexdigest()
    database.execute("INSERT INTO users (email, full_name, phone_number, `password`) VALUES (%s, %s, %s, %s);", (user.email, user.full_name, user.phone_number, hashed_password))
    return {"status": "true", "message": "User created successfully."}


@app.post("/login/")
def login(login: Login):
    global database
    if login.email and login.phone_number:
        return {"status": "false", "message": "You can't use both email and phone number."}
    else:
        if str(login.email or '') == '' and str(login.phone_number or '') == '':
            return {"status": "false", "message": "You must provide either email or phone number."}
        if login.email is not None:
            if not database.fetch_one("SELECT * FROM users WHERE email = %s;", (login.email,)):
                return {"status": "false", "message": "Email doesn't exist."}
        if login.phone_number is not None:
            if not database.fetch_one("SELECT * FROM users WHERE phone_number = %s;", (login.phone_number,)):
                return {"status": "false", "message": "Phone number doesn't exist."}
        if login.password is None:
            return {"status": "false", "message": "You must provide a password."}
        
        hashed_password = hashlib.md5((login.password + salt).encode()).hexdigest()
        if login.email:
            user = database.fetch_one("SELECT * FROM users WHERE email = %s AND `password` = %s;", (login.email, hashed_password))
        else:
            user = database.fetch_one("SELECT * FROM users WHERE phone_number = %s AND `password` = %s;", (login.phone_number, hashed_password))
        if user:
            return {"status": "true", "message": "Login successful."}
        else:
            return {"status": "false", "message": "Incorrect password."}    