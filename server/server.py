# server.py

import socket
import threading
import json
from db import create_user, verify_user, save_message, get_messages_after


HOST = "127.0.0.1"   # Localhost
PORT = 5000          # Server port


clients = {}         # {username: conn}
last_message_id = 0  # For message polling


# -----------------------------
# Helper: Send JSON to client
# -----------------------------
def send_json(conn, data):
    conn.sendall((json.dumps(data) + "\n").encode())


# -----------------------------
# Handle each connected client
# -----------------------------
def handle_client(conn, addr):
    global last_message_id
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

                # -----------------------------
                # REGISTER USER
                # -----------------------------
                if action == "register":
                    user = msg["username"]
                    pasw = msg["password"]

                    ok, info = create_user(user, pasw)
                    send_json(conn, {"response": "register", "success": ok, "info": info})

                # -----------------------------
                # LOGIN USER
                # -----------------------------
                elif action == "login":
                    user = msg["username"]
                    pasw = msg["password"]

                    if verify_user(user, pasw):
                        username = user
                        clients[username] = conn
                        send_json(conn, {"response": "login", "success": True})
                    else:
                        send_json(conn, {"response": "login", "success": False})

                # -----------------------------
                # SEND MESSAGE
                # -----------------------------
                elif action == "send_message":
                    content = msg["content"]

                    save_message(username, content)
                    last_message_id += 1

                    # broadcast to all
                    for user_conn in clients.values():
                        send_json(user_conn, {
                            "response": "new_message",
                            "from": username,
                            "content": content
                        })

                # -----------------------------
                # POLLING: Get new messages
                # -----------------------------
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
    finally:
        if username and username in clients:
            del clients[username]
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")
        

# -----------------------------
# Server Startup
# -----------------------------
def start_server():
    print("[STARTING SERVER] Chat Server running...")

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
