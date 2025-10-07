import json
from db import Database

async def handle_register(data, websocket):
    username = data.get("username")
    password_hash = data.get("password_hash")

    with Database() as db:
        if not db:
            await websocket.send(json.dumps({"type": "auth_response", "status": "SERVER_ERROR"}))
            return

        query_check = "SELECT userName FROM usuarios WHERE userName = %s;"
        if db.fetch_all(query_check, (username,)):
            await websocket.send(json.dumps({"type": "auth_response", "status": "REGISTER_FAILED:USERNAME_EXISTS"}))
        else:
            query_insert = "INSERT INTO usuarios (userName, senha) VALUES (%s, %s);"
            db.execute_query(query_insert, (username, password_hash))
            await websocket.send(json.dumps({"type": "auth_response", "status": "REGISTER_SUCCESS"}))


async def handle_login(data, websocket, online_clients):
    username = data.get("username")
    password_hash = data.get("password_hash")

    with Database() as db:
        if not db:
            await websocket.send(json.dumps({"type": "auth_response", "status": "SERVER_ERROR"}))
            return None

        query = "SELECT senha FROM usuarios WHERE userName = %s;"
        result = db.fetch_all(query, (username,))
        
        if result and result[0]['senha'] == password_hash:
            online_clients[username] = websocket
            await websocket.send(json.dumps({"type": "auth_response", "status": "LOGIN_SUCCESS"}))
            return username  
        else:
            await websocket.send(json.dumps({"type": "auth_response", "status": "LOGIN_FAILED"}))
            return None 