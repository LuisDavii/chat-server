# Ficheiro do servidor Python (server.py)

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from db import Database

class Servidor:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.clients = {} 

    # LÓGICA DE REGISTO
    def handle_register(self, client_socket):
        print("[*] Iniciando processo de registo.")
        username = client_socket.recv(1024).decode('utf-8')
        password = client_socket.recv(1024).decode('utf-8')
        

        print(f"[*] Tentativa de registo do usuário: {username}")
        
        with Database() as db:
            if not db:
                client_socket.send("SERVER_ERROR".encode('utf-8'))
                return

            # VERIFICA SE O USERNAME JÁ EXISTE
            query_check = "SELECT userName FROM usuarios WHERE userName = %s;"
            existing_user = db.fetch_all(query_check, (username,))
            
            if existing_user and len(existing_user) > 0:
                print(f"[FALHA DE REGISTO] Username '{username}' já existe.")
                client_socket.send("REGISTER_FAILED:USERNAME_EXISTS".encode('utf-8'))
            else:
                # Se não existir, insere o novo usuário
                query_insert = "INSERT INTO usuarios (userName, senha) VALUES (%s, %s);"
                db.execute_query(query_insert, (username, password))
                print(f"[SUCESSO DE REGISTO] Usuário '{username}' criado.")
                client_socket.send("REGISTER_SUCCESS".encode('utf-8'))

    # LÓGICA DE LOGIN
    def handle_login(self, client_socket):
        username = client_socket.recv(1024).decode('utf-8')
        password = client_socket.recv(1024).decode('utf-8')

        with Database() as db:
            if not db:
                client_socket.send("SERVER_ERROR".encode('utf-8'))
                return

            query = "SELECT userName FROM usuarios WHERE userName = %s AND senha = %s;"
            result = db.fetch_all(query, (username, password))
            
            if result and len(result) > 0:
                client_socket.send("LOGIN_SUCCESS".encode('utf-8'))
            else:
                client_socket.send("LOGIN_FAILED".encode('utf-8'))

    # DIRECIONADOR DE CLIENTES
    def handle_client(self, client_socket):
        try:
            # 1. Lê o comando inicial (LOGIN ou REGISTER)
            command = client_socket.recv(1024).decode('utf-8')

            if command == "LOGIN":
                print(f"[*] Pedido de LOGIN recebido.")
                
                self.handle_login(client_socket)
            elif command == "REGISTER":
                print(f"[*] Pedido de REGISTO recebido.")
                 
                self.handle_register(client_socket)
            else:
                print(f"[AVISO] Comando desconhecido recebido: {command}")
                
                
        except Exception as e:
            print(f"[ERRO] Erro ao lidar com o cliente: {e}")
        finally:
            client_socket.close()
            print("[*] Conexão com o cliente fechada.")
            

    def start(self):
        server = socket(AF_INET, SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()
        print(f"[*] Ouvindo em {self.host}:{self.port}")

        while True:
            client_socket, addr = server.accept()
            print(f"[*] Conexão aceita com {addr}")
            client_handler = Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    servidor = Servidor()
    servidor.start()