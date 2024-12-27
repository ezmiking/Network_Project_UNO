import socket
import threading
from uno.uno import *

HOST = '127.0.0.1'
PORT = 12345

clients = []

def broadcast(message, sender_socket=None):
    """Broadcast a message to all clients except the sender."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error sending message: {e}")
                clients.remove(client)


def handle_client(client_socket, game: UnoGame, ):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')

            if not message:
                raise Exception("Empty message received")


            if game.current_player.player_id == clients.index(client_socket):
                print(f"Player {clients.index(client_socket)} played: {message}")

                if message == "pickup":
                    game.play(player=game.current_player.player_id, card=None)

                    for client in clients:
                        client.send(f"Player {clients.index(client_socket)} picked up a card".encode('utf-8'))

                else:

                    card_color = message.split()[0]
                    card_value = message.split()[1]
                    new_color = ''
                    if len(message.split()) == 3:
                        new_color = message.split()[2]

                    if not (
                            card_value == 'reverse' or card_value == 'skip' or card_value == '+2' or card_value == 'wildcard' or card_value == '+4'):
                        card_value = int(card_value)

                    doesItPlayed = 0
                    for card in game.current_player.hand:
                        if card.color == card_color and card.card_type == card_value and game.current_card.playable(card):
                            if card.color == 'black':
                                game.play(player=game.current_player.player_id,
                                          card=game.current_player.hand.index(card), new_color=new_color)
                                doesItPlayed = 1
                                break

                            else:
                                game.play(player=game.current_player.player_id,
                                          card=game.current_player.hand.index(card))
                                doesItPlayed = 1
                                break

                    if doesItPlayed == 0:
                        continue

                    for client in clients:
                        client.send(f"Player {clients.index(client_socket)} played: {message}\ncurrent card: {game.current_card}".encode('utf-8'))

                clients[game.current_player.player_id].send(f"your hand: {game.current_player.hand}\nYour turn !".encode('utf-8'))

            else:
                print(f"Player {clients.index(client_socket)} tried to play out of turn.")
                client_socket.send("Not your turn!".encode('utf-8'))

        except Exception as e:
            print(f"Client {clients.index(client_socket)} disconnected: {e}")

            break

def handel_game():
    game = UnoGame(4)
    for client in clients:
        client.send(f"{game.players[clients.index(client)].hand}".encode('utf-8'))
        threading.Thread(target=handle_client, args=(client,game,)).start()

def start_server():
    """Start the chat server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept()
        print(f"New connection from {client_address}")
        clients.append(client_socket)
        if len(clients) == 4:
            print("khkhkhkhkhkhk")
            threading.Thread(target=handel_game(), args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
