"""
TCP chat server for the multi-user chatroom application.

This server:
- Accepts client connections over TCP.
- Handles login and registration.
- Stores messages in the database.
- Broadcasts new messages to all connected users.
- Supports polling for message history.
"""

import socket
import threading
import json
from db import create_user, verify_user, save_message, get_messages_after
from models import init_db


HOST = "0.0.0.0"
PORT = 5000


clients = {}    # Here we are storing the clients


def send_json(conn, data):
    """
    Here we are sending a Python dictionary as a JSON message terminated by a newline.

    Args:
        conn (socket.socket): The connection to send through.
        data (dict): The JSON-serializable data to send.
    """
    conn.sendall((json.dumps(data) + "\n").encode())


def handle_client(conn, addr):
    """
    Here we are handling communication with a single connected client.

 
    """
    print(f"[NEW CONNECTION] {addr} connected.")

    username = None

    try:
        while True:
            data = conn.recv(1024).decode()

            if not data:
                break

            for line in data.strip().split("\n"):
                msg = json.loads(line)

                action = msg.get("action")

                # Here we are handling the registration flow
                if action == "register":
                    user = msg["username"]
                    pasw = msg["password"]

                    ok, info = create_user(user, pasw)
                    send_json(conn, {"response": "register", "success": ok, "info": info})

                # Here we are handling the login flow
                elif action == "login":
                    user = msg["username"]
                    pasw = msg["password"]

                    if verify_user(user, pasw):
                        username = user
                        clients[username] = conn
                        send_json(conn, {"response": "login", "success": True})
                    else:
                        send_json(conn, {"response": "login", "success": False})

                # Here we are handling the sending of messages
                elif action == "send_message":
                    content = msg["content"]

                    msg_id, ts = save_message(username, content)

                    # Here we are broadcasting the message to all clients
                    for user_conn in clients.values():
                        send_json(user_conn, {
                            "response": "new_message",
                            "id": msg_id,
                            "from": username,
                            "content": content,
                            "timestamp": ts
                        })

                # Here we are polling the server for new messages
                elif action == "poll":
                    last_id = msg.get("last_id", 0)
                    messages = get_messages_after(last_id)

                    response = []
                    for m in messages:
                        response.append({
                            "id": m.id,
                            "sender": m.sender,
                            "content": m.text,
                            "timestamp": str(m.timestamp)
                        })

                    send_json(conn, {"response": "poll", "messages": response})

                # Here we are handling unknown actions
                else:
                    send_json(conn, {"response": "error", "info": "Unsupported action"})
    finally:
        if username and username in clients:
            del clients[username]
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")
        

def start_server():
    """
    Here we are starting the TCP server.
   
    """
    print("[STARTING SERVER] Chat Server running...")
    init_db()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[LISTENING] Server running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    start_server()
