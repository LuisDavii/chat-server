import asyncio
import json
from db import Database

async def broadcast_user_list(online_clients):
    """Envia a lista atualizada de usuários para todos os clientes online."""
    if not online_clients:
        return

    print("[Broadcast] Enviando lista de usuários atualizada...")
    all_users = []
    with Database() as db:
        if db:
            
            rows = db.fetch_all("SELECT userName FROM usuarios;")
            all_users = [row['userName'] for row in rows]
    
    # online ou offline
    user_status_list = [
        {"username": user, "isOnline": user in online_clients} for user in all_users
    ]
    
    message = {"type": "user_list_update", "users": user_status_list}
    
    # Envia a mensagem para todos
    await asyncio.gather(
        *[client.send(json.dumps(message)) for client in online_clients.values()]
    )

async def handle_chat_session(websocket, username, online_clients):
    """
    Lida com o loop de mensagens de um usuário já autenticado.
    Esta função é chamada depois que o login é bem-sucedido.
    """
    print(f"[Chat] Iniciando sessão de chat para '{username}'.")
    async for message in websocket:
        chat_data = json.loads(message)
        command = chat_data.get("type")

        if command == "REQUEST_USER_LIST":
            await broadcast_user_list(online_clients)
            
            # manda mensagens de chat
        elif command == "chat_message":
            recipient = chat_data.get("to")
            
            chat_message = {
                "type": "chat_message",
                "from": username,
                "content": chat_data.get("content")
            }
            
            if recipient in online_clients:
                await online_clients[recipient].send(json.dumps(chat_message))
                print(f"[Chat] Mensagem de '{username}' para '{recipient}'.")