# Project Title
Multiplayer UNO Game with Authentication

## Description
This project is a multiplayer UNO game implemented in Python. It features:
- A server that handles game logic, authentication, and player interactions.
- A client for players to connect to the server and participate in the game.
- Token-based authentication using JWT for secure login and sign-up.
- Database support for storing user details, including wins and losses.

## Features
- **Game Logic**: Implements the full rules of UNO.
- **Authentication**: Users can sign up and log in using JWT tokens.
- **Leaderboard**: Displays user rankings based on wins and losses.
- **Chat**: Supports public and private messaging between players.

## Technologies Used
- **Python**: Main programming language.
- **Socket Programming**: For real-time communication between clients and the server.
- **JWT (JSON Web Tokens)**: For secure authentication.
- **SQLAlchemy**: For database operations.
- **SQLite**: Default database (can be replaced with other databases).

## Folder Structure
```
pythonProject/
├── create_table.py      # Script for creating database tables
├── database.py          # Database connection and session management
├── models.py            # ORM models for database
├── server.py            # Main server script
├── user.py              # User-related logic
├── uno/                 # Contains the UNO game logic
├── Simple chat/         # Additional chat functionality
├── .git/                # Git version control
├── .venv/               # Virtual environment for dependencies
├── .idea/               # IDE configuration (PyCharm)
```

## Setup Instructions
### Prerequisites
- Python 3.8 or later
- Virtual environment tool (e.g., `venv` or `virtualenv`)

### Installation
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd pythonProject
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python create_table.py
   ```

### Running the Server
1. Start the server:
   ```bash
   python server.py
   ```
   The server will start listening on `127.0.0.1:12345`.

### Running the Client
1. Start the client:
   ```bash
   python client.py
   ```

2. Follow the prompts to sign up or log in.
3. Once authenticated, participate in the game and chat.

## Usage
### Commands
- **Play**: Send the appropriate card or command (`pickup`, `color value new_color`).
- **Chat**:
  - Public: `chat <message>`
  - Private: `chat P <username> <message>`
- **Leaderboard**: `LW`

## Notes
- Maximum of 4 players can participate in a game.
- Ensure the database is set up before starting the server.
- Use private messaging responsibly.

## Future Enhancements
- Add support for more players.
- Enhance UI for a better user experience.
- Add advanced error handling and logging.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

