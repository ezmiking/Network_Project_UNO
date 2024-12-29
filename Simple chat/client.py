import socket
import threading

HOST = '127.0.0.1'  # Server address
PORT = 12345        # Server port

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("Disconnected from the server.")
                client_socket.close()
                break
            print(message)
        except:
            print("Disconnected from the server.")
            client_socket.close()
            break

def send_messages(client_socket):
    while True:
        message = input()
        try:
            client_socket.send(message.encode('utf-8'))
        except:
            print("Disconnected from the server.")
            client_socket.close()
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Connected to server at {HOST}:{PORT}")

    while True:
        print("Do you want to (1) Login or (2) Sign up?")
        choice = input("Enter 1 or 2: ").strip()
        if choice not in ["1", "2"]:
            print("Invalid choice, try again.")
            continue

        username = input("Username: ").strip()
        password = input("Password: ").strip()

        if choice == "1":
            auth_type = "login"
        else:
            auth_type = "signup"

        auth_message = f"AUTH {auth_type} {username} {password}"
        client_socket.send(auth_message.encode('utf-8'))

        server_response = client_socket.recv(1024).decode('utf-8')
        print("Server Response:", server_response)

        if server_response.startswith("AUTH_SUCCESS"):
            print("Authentication successful! You can now play.")
            break
        else:
            print("Authentication failed or user already exists. Try again.")

    # آغاز Thread دریافت پیام‌ها
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
    # آغاز حلقهٔ ارسال پیام‌ها
    send_messages(client_socket)

if __name__ == "__main__":
    start_client()
