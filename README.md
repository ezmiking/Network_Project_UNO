# Uno Multiplayer Game with Save and Load Functionality

## Overview

This project implements a multiplayer Uno game with server-client architecture. It features user authentication, a leaderboard, real-time gameplay, and the ability to save and load game states. The project uses sockets for communication and JWT for secure authentication.

---

## Features

### General Features

- **Multiplayer Gameplay**: Up to 4 players can connect to the server and play Uno.
- **Real-Time Chat**: Players can communicate via public and private messages.
- **Leaderboard**: Tracks wins and losses for all users in the database.
- **Save & Load Game**: Players can save the current game state to a database and reload it later.

### Security Features

- **Authentication**: Supports user sign-up and login with JWT-based authentication.
- **Unique Sessions**: Prevents multiple logins with the same username in the same game session.

---

## Requirements

### Server

- Python 3.8+
- Libraries:
  - `socket`
  - `threading`
  - `jwt`
  - `sqlalchemy`
  - `datetime`
- Additional Modules:
  - `UnoGame`, `UnoCard` from `uno.uno`
  - `SessionLocal` from `database`
  - `User`, `SaveGame` models

### Client

- Python 3.8+
- Libraries:
  - `socket`
  - `threading`

---

## Setup and Usage

### Server

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install pyjwt sqlalchemy
   ```
3. Ensure that the database is properly configured and includes `User` and `SaveGame` tables.
4. Start the server:
   ```bash
   python server.py
   ```

The server listens on `127.0.0.1:12345` by default.

### Client

1. Clone the repository.
2. Start the client:
   ```bash
   python client.py
   ```
3. Connect to the server and follow the prompts to log in or sign up.

---

## How to Play

### Authentication

- At the start, users are prompted to log in or sign up.
- Users must provide a unique username and password.
- Successful authentication generates a JWT token.

### Gameplay

1. Once 4 players are authenticated, the game begins.
2. Each player receives their initial hand and the current card is announced.
3. Players take turns to:
   - Play a valid card.
   - Pick up a card if no valid move is available.
4. The game ends when a player plays all their cards.
5. The winner is recorded in the leaderboard, and all other players receive a loss.

### Chat Commands

- **Public Chat**: `chat <message>`
- **Private Chat**: `chat P <username> <message>`

### Save & Load

- To save the game: `save`
- To load a saved game: All players must agree to load the last saved state.

---

## Code Structure

### Server

- **Authentication**: Handles user sign-up, login, and JWT generation.
- **Game Logic**: Manages the flow of the Uno game and ensures rules are followed.
- **Database Operations**:
  - Save game state.
  - Load game state.
  - Update leaderboard.

### Client

- **Message Handling**: Sends user inputs to the server and displays server responses.
- **Authentication**: Prompts users for login or sign-up details.
- **Gameplay Interaction**: Allows users to play cards, chat, and save games.

---

## Future Enhancements

- Implement GUI for client-side interactions.
- Add support for additional Uno variants.
- Enhance security with password hashing.

---

## Known Issues

- The game does not validate card play extensively on the client-side.
- Relies on all players to be online for the saved game to load correctly.

---

## Contributors

Amirreza Khadempir - Developer

---

## License

This project is licensed under the MIT License.

