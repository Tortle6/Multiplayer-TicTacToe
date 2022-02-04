import socket
import time
import threading
import pickle

you = "X"
opponent = "O"
turn = opponent
start_player = you

board = [[" " for i in range(3)] for x in range(3)]
moves = 0

HEADERSIZE = 64

PORT = 1234
IP = "YOUR LOCAL IP"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT))
s.listen(2)

clients = []


def manage_clients():
    clientsocket, address = s.accept()

    if len(clients) > 1:
        clientsocket.close()

    else:
        clients.append(clientsocket)


def print_board(current_board):
    for i in range(3):
        for x in range(3):
            if x != 2:
                print(current_board[i][x], end=" | ")
            else:
                print(current_board[i][x])

        if i != 2:
            print("----------")


def win_check():
    # Check columns
    if board[0][0] == board[0][1] == board[0][2] != " ":
        return f"{board[0][0]} wins!"

    if board[1][0] == board[1][1] == board[1][2] != " ":
        return f"{board[1][0]} wins!"

    if board[2][0] == board[2][1] == board[2][2] != " ":
        return f"{board[2][0]} wins!"

    # Check rows

    if board[0][0] == board[1][0] == board[2][0] != " ":
        return f"{board[0][0]} wins!"

    if board[0][1] == board[1][1] == board[2][1] != " ":
        return f"{board[0][1]} wins!"

    if board[0][1] == board[1][1] == board[2][1] != " ":
        return f"{board[0][2]} wins!"

    # Check diagonals

    if board[0][0] == board[1][1] == board[2][2] != " ":
        return f"{board[0][0]} wins!"

    if board[0][2] == board[1][1] == board[2][0] != " ":
        return f"{board[0][0]} wins!"

    # Check tie

    if moves >= 9:
        return "Tie"

    return "no winner"


def valid_move(x, y):
    return board[y][x] == " "


def restart_game():  # Restart the round and switch which player goes first
    global start_player, turn, board, moves
    print_board(board)
    print(f"{win_check()}\n")

    if start_player == you:
        turn = you
        start_player = opponent

    else:
        turn = opponent
        start_player = you

    board = [[" " for i in range(3)] for x in range(3)]
    moves = 0
    time.sleep(2)


t = threading.Thread(target=manage_clients)
t.start()


if __name__ == "__main__":
    print("Waiting for player to connect...")

    # Wait for player
    while len(clients) < 1:
        time.sleep(1)

    client_socket = clients[0]

    print("Opponent connected.")

    while True:
        if turn == opponent:
            turn = you

            # Record the host's move
            while True:
                while True:
                    try:
                        print_board(board)
                        move = input("Enter a move (x, y): ")
                        move = move.split()
                        move_x = int(move[0][0]) - 1
                        move_y = int(move[1]) - 1
                        break

                    except ValueError or IndexError:
                        print("Please input valid formatting: \"x, y\"")

                # Check if the move is valid
                if valid_move(move_x, move_y):
                    board[move_y][move_x] = turn
                    moves += 1
                    break

                # If move is invalid, ask for a different move.
                else:
                    print("Invalid move.")
                    continue

            # Send to the client if the host won
            client_socket.send(win_check().encode("utf-8"))
            if win_check() != "no winner":
                restart_game()

        else:

            # Send board information to the client and wait for a response
            turn = opponent
            msg = pickle.dumps(board)
            client_socket.send(msg)
            print("Waiting for opponent...")

            opponent_moves = client_socket.recv(HEADERSIZE)

            moves += 1
            # Recieve and process move information sent by the client.
            opponent_moves = pickle.loads(opponent_moves)
            opponent_move_x = opponent_moves[0]
            opponent_move_y = opponent_moves[1]

            if valid_move(opponent_move_x, opponent_move_y):
                board[opponent_move_y][opponent_move_x] = turn

            # Send to the client if they won.

            client_socket.send(win_check().encode("utf-8"))
            if win_check() != "no winner":
                restart_game()

                print(f"Start player: {start_player} Turn: {turn}")

                board = [[" " for i in range(3)] for x in range(3)]
                moves = 0

                time.sleep(3)
