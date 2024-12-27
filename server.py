import socket
import threading

from uno.uno import *
from database import SessionLocal
from models import User

HOST = '127.0.0.1'
PORT = 12345

clients = []
authenticated_users = []

def broadcast(message, sender_socket=None):
    """Broadcast a message to all clients except the sender."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error sending message: {e}")
                clients.remove(client)

def authenticate_client(client_socket):
    """
    منتظر پیام AUTH از سمت کلاینت می‌مانیم. سپس در دیتابیس
    صحت اطلاعات را بررسی می‌کنیم و در صورت موفقیت، AUTH_SUCCESS می‌فرستیم
    وگرنه پیام خطا.
    برمی‌گرداند: (bool, username)
    bool = True اگر احراز هویت موفق بود، False اگر شکست خورد.
    """
    try:
        # منتظر COMMAND اول از کلاینت می‌شویم (AUTH ...)
        data = client_socket.recv(1024).decode('utf-8').strip()
        if not data:
            return False, None

        parts = data.split()
        if len(parts) != 4:
            # فرمت AUTH <login|signup> <username> <password>
            client_socket.send("AUTH_FAILED Invalid format\n".encode('utf-8'))
            return False, None

        if parts[0] != "AUTH":
            client_socket.send("AUTH_FAILED Missing AUTH keyword\n".encode('utf-8'))
            return False, None

        auth_type = parts[1]  # login یا signup
        username = parts[2]
        password = parts[3]

        # حالا با دیتابیس چک می‌کنیم
        db = SessionLocal()
        user_in_db = db.query(User).filter_by(username=username).first()

        if auth_type.lower() == 'signup':
            # اگر وجود دارد، ارور بده
            if user_in_db:
                client_socket.send("AUTH_FAILED User already exists.\n".encode('utf-8'))
                db.close()
                return False, None
            # وگرنه بساز
            new_user = User(username=username, password=password)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            client_socket.send("AUTH_SUCCESS Signup successful.\n".encode('utf-8'))
            db.close()
            return True, username

        elif auth_type.lower() == 'login':
            # اگر پیدا نشد یا پسورد غلط بود
            if not user_in_db or user_in_db.password != password:
                client_socket.send("AUTH_FAILED Invalid username or password.\n".encode('utf-8'))
                db.close()
                return False, None

            # در صورت موفقیت
            client_socket.send("AUTH_SUCCESS Login successful.\n".encode('utf-8'))
            db.close()
            return True, username

        else:
            client_socket.send("AUTH_FAILED Invalid auth type.\n".encode('utf-8'))
            db.close()
            return False, None

    except Exception as e:
        print(f"Error in authenticate_client: {e}")
        client_socket.send(f"AUTH_FAILED Internal error: {e}\n".encode('utf-8'))
        return False, None


def handle_client(client_socket, game: UnoGame):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')

            if not message:
                raise Exception("Empty message received")

            if message == "kir":
                # client_socket.send("KIR SUCCESS\n".encode('utf-8'))
                pass
            print(message)
            if message.split()[0] == "chat":
                for client in clients:
                    client.send(f"{message.split()[1]}".encode('utf-8'))
                continue

            if game.current_player.player_id == clients.index(client_socket):
                print(f"Player {clients.index(client_socket)} played: {message}")

                if message == "pickup":
                    game.play(player=game.current_player.player_id, card=None)

                    for client in clients:
                        client.send(f"Player {clients.index(client_socket)} picked up a card".encode('utf-8'))

                else:
                    parts = message.split()
                    if len(parts) < 2:
                        continue
                    card_color = parts[0]
                    card_value = parts[1]
                    new_color = ''
                    if len(parts) == 3:
                        new_color = parts[2]

                    if card_value.isdigit():
                        card_value = int(card_value)

                    doesItPlayed = False
                    for card in game.current_player.hand:
                        if card.color == card_color and card.card_type == card_value and game.current_card.playable(card):
                            if card.color == 'black':
                                game.play(player=game.current_player.player_id,
                                          card=game.current_player.hand.index(card),
                                          new_color=new_color)
                            else:
                                game.play(player=game.current_player.player_id,
                                          card=game.current_player.hand.index(card))
                            doesItPlayed = True
                            break

                    if not doesItPlayed:
                        client_socket.send("Invalid card or not playable.\n".encode('utf-8'))
                        continue

                    for client in clients:
                        client.send(f"Player {clients.index(client_socket)} played: {message}\n"
                                    f"current card: {game.current_card}\n".encode('utf-8'))


                clients[game.current_player.player_id].send(
                    f"your hand: {game.current_player.hand}\nYour turn !".encode('utf-8')
                )
            else:
                print(f"Player {clients.index(client_socket)} tried to play out of turn.")
                client_socket.send("Not your turn!\n".encode('utf-8'))

        except Exception as e:
            print(f"Client {clients.index(client_socket)} disconnected: {e}")
            break


def handel_game():
    game = UnoGame(4)

    for i, client in enumerate(clients):
        client.send(f"{game.players[i].hand}\n".encode('utf-8'))
        client.send(f"current cort {game.current_card.color} {game.current_card.card_type}".encode('utf-8'))
        # client.socket.send(f"current cort{game.current_card}")
        threading.Thread(target=handle_client, args=(client, game,)).start()


def start_server():
    """Start the chat server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept()
        print(f"New connection from {client_address}")

        # پیش از پذیرش کلاینت به بازی، باید احراز هویت کند
        success, username = authenticate_client(client_socket)
        if success:
            print(f"[+] Auth success for user '{username}' from {client_address}")
            # اگر موفق بود، اضافه به لیست clients
            clients.append(client_socket)
            authenticated_users.append(username)

            # اگر به چهار نفر رسیدیم، بازی را شروع کنیم
            if len(clients) == 4:
                print("4 players connected. Starting the game...")
                handel_game()
        else:
            print(f"[-] Auth failed from {client_address}, closing socket.")
            client_socket.close()
            continue


if __name__ == "__main__":
    start_server()
