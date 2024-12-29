import socket
import threading

from uno.uno import UnoGame
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
                print(f"Error sending message to a client: {e}")
                if client in clients:
                    clients.remove(client)

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

            client_socket.send(b"AUTH_SUCCESS Signup successful.\n")
            db.close()
            return True, username

        elif auth_type == 'login':
            if not user_in_db or user_in_db.password != password:
                client_socket.send(b"AUTH_FAILED Invalid username or password.\n")
                db.close()
                return False, None

            client_socket.send(b"AUTH_SUCCESS Login successful.\n")
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
            print(f"Received from {clients.index(client_socket)}: {message}")

            if message.upper() == "LW":
                with SessionLocal() as db:
                    users = db.query(User).all()
                    scoreboard = "\n--- Leaderboard (All Users) ---\n"
                    for u in users:
                        scoreboard += f"User: {u.username}, Wins: {u.wins}, Losses: {u.losses}\n"
                client_socket.send(scoreboard.encode('utf-8'))
                continue

            parts = message.split(maxsplit=1)
            if len(parts) > 0 and parts[0].lower() == "chat":
                if len(parts) == 1:
                    client_socket.send(b"No chat message provided.\n")
                else:
                    chat_msg = f"[CHAT] Player {clients.index(client_socket)}: {parts[1]}"
                    broadcast(chat_msg.encode('utf-8'))
                continue

            if game.current_player.player_id == clients.index(client_socket):

                if message == "pickup":
                    game.play(player=game.current_player.player_id, card=None)
                    broadcast(
                        f"Player {clients.index(client_socket)} picked up a card\n".encode('utf-8')
                    )

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
                        if (c.color == card_color
                                and c.card_type == card_value
                                and game.current_card.playable(c)):
                            if c.color == 'black':
                                game.play(player=game.current_player.player_id,card=game.current_player.hand.index(c),
                                    new_color=new_color
                                )
                            else:
                                game.play(player=game.current_player.player_id, card=game.current_player.hand.index(c))
                            doesItPlayed = True
                            break

                    if not doesItPlayed:
                        client_socket.send(b"Invalid card or not playable.\n")
                        continue

                    broadcast(f"Player {clients.index(client_socket)} played: {message}\n"f"Current card: {game.current_card}\n".encode('utf-8'))

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
            print(f"[!] Client {clients.index(client_socket)} disconnected: {e}")
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
    """Start the Uno server and wait for 4 players."""
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
