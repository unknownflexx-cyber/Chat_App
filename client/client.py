import socket
import json
import sys
import threading
import time

HOST = "127.0.0.1"  
PORT = 5000              

last_message_id = 0         
stop_event = threading.Event()
current_username = ""


# Here we are sending the JSON data to the server

def send_json(conn, data: dict):
    """
    Here we are sending a JSON object followed by newline (server expects line-delimited JSON).
    """
    conn.sendall((json.dumps(data) + "\n").encode())



# Here we are receiving the data from the server. This function is used to receive one line of data from the server.
def recv_one_line(conn: socket.socket):
    """
    Here we are receiving one line of data from the server.
    """
    data = conn.recv(4096).decode()
    if not data:
        return None
    return json.loads(data.split("\n")[0])


# Here we are receiving the data from the server. This thread is the ONLY place that calls recv().
def receiver_loop(conn: socket.socket):
    """
    Here we are receiving the data from the server. This thread is the ONLY place that calls recv().
    It handles:
      - broadcast messages: response == "new_message"
      - poll responses:     response == "poll"
    """
    global last_message_id

    try:
        while not stop_event.is_set():
            data = conn.recv(4096).decode()

            # If connection is closed or no data, keep looping (or break)
            if not data:
                continue

            # Server sends one JSON per line
            for line in data.strip().split("\n"):
                if not line.strip():
                    continue

                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                rtype = msg.get("response")

                # Broadcast message from server
                if rtype == "new_message":
                    sender = msg.get("from", "???")
                    content = msg.get("content", "")
                    mid = msg.get("id", 0)
                    # Deduplicate against poll results by checking id progression
                    if mid > last_message_id:
                        if sender != current_username:
                            print(f"\n[{sender}] {content}")
                        last_message_id = mid
                        print("> ", end="", flush=True)

                # Poll response (history)
                elif rtype == "poll":
                    messages = msg.get("messages", [])
                    for m in messages:
                        sender = m.get("sender", "???")
                        content = m.get("content", "")
                        mid = m.get("id", 0)
                        # Print only unseen messages
                        if mid > last_message_id:
                            print(f"\n[{sender}] {content}")
                            last_message_id = mid
                    if messages:
                        print("> ", end="", flush=True)

                # Other responses ignored (login/register handled before threads)
    except OSError:
        # Socket closed, exit thread
        pass


# Here we are polling the server for new messages
def poll_loop(conn: socket.socket):
    global last_message_id

    while not stop_event.is_set():
        try:
            send_json(conn, {
                "action": "poll",
                "last_id": last_message_id
            })
        except OSError:
            break

        time.sleep(1)


# Here we are handling the login and registration flow
def auth_flow(conn: socket.socket):
    """
    Here we are handling the menu for login/register.
    Here we are running before starting the receiver threads.
    """
    while True:
        print("\n1. Login")
        print("2. Register")
        choice = input("Choose (1/2): ").strip()

    # Here we are validating the menu choice
        if choice not in ("1", "2"):
            print("❌ Invalid choice. Please enter 1 or 2.\n")
            continue

    # Here we are handling the login flow
        if choice == "1":
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            send_json(conn, {
                "action": "login",
                "username": username,
                "password": password
            })

            resp = recv_one_line(conn)
            if not resp:
                print("No response from server.")
                continue

            if resp.get("response") == "login" and resp.get("success"):
                print("✅ Login successful!\n")
                return username
            else:
                print("❌ Incorrect username or password.\n")
                # loop back to menu

 # Here we are handling the registration flow
        elif choice == "2":
            # Username validation (min 3 chars)
            while True:
                username = input("Choose a username: ").strip()
                if len(username) < 3:
                    print("❌ Username must be at least 3 characters long.")
                    continue
                break

            # Password validation (min 8 chars)
            while True:
                password = input("Choose a password: ").strip()
                if len(password) < 8:
                    print("❌ Password must be at least 8 characters long.")
                    continue
                break

            send_json(conn, {
                "action": "register",
                "username": username,
                "password": password
            })

            resp = recv_one_line(conn)
            if not resp:
                print("No response from server.")
                continue

            if resp.get("response") == "register":
                # Server sends "info" like: "User created successfully" or error
                print(resp.get("info", "No message from server."))
            else:
                print("Unexpected response from server.")

            # Here we are going back to the menu


# Here we are the main function of the client
def main():
    global stop_event, current_username

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((HOST, PORT))
    print(f"Connected to chat server at {HOST}:{PORT}")

    # Here we are handling the login and registration flow
    username = auth_flow(conn) 
    current_username = username

    # Here we are starting the receiver and poll threads
    recv_thread = threading.Thread(target=receiver_loop, args=(conn,), daemon=True)
    recv_thread.start()
    poll_thread = threading.Thread(target=poll_loop, args=(conn,), daemon=True)     
    poll_thread.start()

    print("=== Welcome to the Chat Room ===")
    print("Type your messages and press Enter.")
    print("Press Ctrl+C to exit.\n")

    try:
        while True:
            msg = input("> ")
            if not msg.strip():
                continue

            send_json(conn, {
                "action": "send_message",
                "content": msg
            })

    except KeyboardInterrupt:
        print("\nExiting chat...")

    finally:
        stop_event.set()
        try:
            conn.close()
        except OSError:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()