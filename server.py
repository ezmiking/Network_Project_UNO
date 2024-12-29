import socket
import threading

import jwt
import datetime

from uno.uno import UnoGame
from database import SessionLocal
from models import User

HOST = '127.0.0.1'
PORT = 12345

SECRET_KEY = "MY_SECRET_JWT_KEY_123"

clients = []
authenticated_users = []

def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error sending message to a client: {e}")
                if client in clients:
                    clients.remove(client)

# --- TOKEN ADDED ---
def generate_token(username):
    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def authenticate_client(client_socket):
    try:
        data = client_socket.recv(1024).decode('utf-8').strip()
        if not data:
            return False, None

        parts = data.split()
        if len(parts) != 4:
            client_socket.send(b"AUTH_FAILED Invalid format\n")
            return False, None

        if parts[0] != "AUTH":
            client_socket.send(b"AUTH_FAILED Missing AUTH keyword\n")
            return False, None

        auth_type = parts[1].lower()
        username = parts[2]
        password = parts[3]

        db = SessionLocal()
        user_in_db = db.query(User).filter_by(username=username).first()

        if auth_type == 'signup':
            if user_in_db:
                client_socket.send(b"AUTH_FAILED User already exists.\n")
                db.close()
                return False, None

            new_user = User(username=username, password=password, wins=0, losses=0)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            token = generate_token(username)  # --- TOKEN ADDED ---
            client_socket.send(f"AUTH_SUCCESS {token}\n".encode('utf-8'))

            db.close()
            return True, username

        elif auth_type == 'login':
            if not user_in_db or user_in_db.password != password:
                client_socket.send(b"AUTH_FAILED Invalid username or password.\n")
                db.close()
                return False, None

            token = generate_token(username)
            client_socket.send(f"AUTH_SUCCESS {token}\n".encode('utf-8'))

            db.close()
            return True, username

        else:
            client_socket.send(b"AUTH_FAILED Invalid auth type.\n")
            db.close()
            return False, None

    except Exception as e:
        print(f"Error in authenticate_client: {e}")
        client_socket.send(f"AUTH_FAILED Internal error: {e}\n".encode('utf-8'))
        return False, None

def handle_client(client_socket, game: UnoGame):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                raise Exception("Empty message received or client disconnected.")
            message = data.decode('utf-8').strip()

            current_index = clients.index(client_socket)
            print(f"Received from client[{current_index}]: {message}")

            if message.upper() == "LW":
                with SessionLocal() as db:
                    users = db.query(User).all()
                    scoreboard = "\n--- Leaderboard (All Users) ---\n"
                    for u in users:
                        scoreboard += f"User: {u.username}, Wins: {u.wins}, Losses: {u.losses}\n"
                client_socket.send(scoreboard.encode('utf-8'))
                continue

            parts = message.split()
            if len(parts) > 0 and parts[0].lower() == "chat":
                if len(parts) == 1:
                    client_socket.send(b"No chat message provided.\n")
                    continue

                if parts[1].upper() == "P":
                    if len(parts) < 4:
                        client_socket.send(b"Usage: chat P <username> <message>\n")
                        continue

                    target_username = parts[2]
                    private_msg = " ".join(parts[3:])

                    if target_username not in authenticated_users:
                        client_socket.send(f"User '{target_username}' not found.\n".encode('utf-8'))
                        continue

                    target_index = authenticated_users.index(target_username)
                    sender_name = authenticated_users[current_index]
                    final_msg = f"[PRIVATE from {sender_name}] {private_msg}"

                    target_socket = clients[target_index]
                    target_socket.send(final_msg.encode('utf-8'))

                else:
                    chat_msg = " ".join(parts[1:])
                    sender_name = authenticated_users[current_index]
                    broadcast_msg = f"[CHAT from {sender_name}] {chat_msg}"
                    broadcast(broadcast_msg.encode('utf-8'))
                continue

            # کنترل نوبت بازی
            if game.current_player.player_id == current_index:
                if message == "pickup":
                    game.play(player=game.current_player.player_id, card=None)
                    broadcast(f"Player {current_index} picked up a card\n".encode('utf-8'))

                else:
                    card_parts = message.split()
                    if len(card_parts) < 2:
                        client_socket.send(b"Invalid card format.\n")
                        continue
                    card_color = card_parts[0]
                    card_value = card_parts[1]
                    new_color = ''
                    if len(card_parts) == 3:
                        new_color = card_parts[2]

                    if card_value.isdigit():
                        card_value = int(card_value)

                    doesItPlayed = False
                    for c in game.current_player.hand:
                        if (c.color == card_color and
                            c.card_type == card_value and
                            game.current_card.playable(c)):
                            if c.color == 'black':
                                game.play(
                                    player=game.current_player.player_id,
                                    card=game.current_player.hand.index(c),
                                    new_color=new_color
                                )
                            else:
                                game.play(
                                    player=game.current_player.player_id,
                                    card=game.current_player.hand.index(c)
                                )
                            doesItPlayed = True
                            break

                    if not doesItPlayed:
                        client_socket.send(b"Invalid card or not playable.\n")
                        continue

                    broadcast(f"Player {current_index} played: {message}\n"
                              f"Current card: {game.current_card}\n".encode('utf-8'))

                # اتمام بازی
                if not game.is_active:
                    winner_player = game.winner
                    winner_index = game.players.index(winner_player)
                    winner_name = authenticated_users[winner_index]

                    with SessionLocal() as db:
                        winner_user = db.query(User).filter_by(username=winner_name).first()
                        if winner_user:
                            winner_user.wins += 1
                            db.commit()

                        for i, uname in enumerate(authenticated_users):
                            if i != winner_index:
                                loser_user = db.query(User).filter_by(username=uname).first()
                                if loser_user:
                                    loser_user.losses += 1
                                    db.commit()

                    broadcast(f"Game Over! Winner is {winner_name}\n".encode('utf-8'))
                    break

                next_player_id = game.current_player.player_id
                clients[next_player_id].send(
                    f"Your hand: {game.current_player.hand}\nYour turn!\n".encode('utf-8')
                )
            else:
                client_socket.send(b"Not your turn!\n")

        except Exception as e:
            print(f"[!] Client {current_index} disconnected: {e}")
            break

def handel_game():
    game = UnoGame(4)
    for i, client in enumerate(clients):
        client.send(f"Your initial hand: {game.players[i].hand}\n".encode('utf-8'))
        client.send(f"Current card: {game.current_card.color} {game.current_card.card_type}\n".encode('utf-8'))

    for i, client in enumerate(clients):
        t = threading.Thread(target=handle_client, args=(client, game))
        t.start()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept()
        print(f"[+] New connection from {client_address}")

        success, username = authenticate_client(client_socket)
        if success:
            print(f"[+] Auth success for user '{username}' from {client_address}")
            clients.append(client_socket)
            authenticated_users.append(username)

            if len(clients) == 4:
                print("[*] 4 players connected. Starting the game...")
                handel_game()
        else:
            print(f"[-] Auth failed from {client_address}, closing socket.")
            client_socket.close()

if __name__ == "__main__":
    start_server()
