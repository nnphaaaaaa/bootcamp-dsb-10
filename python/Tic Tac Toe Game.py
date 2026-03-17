#create empty Tic Tac Toe board. the board will be a list of 9 elements, representing the 9 squares.

def create_board():
    return [ " " for x in range(9) ]

board = create_board()
print(board)

# create function to display the current state
def display_board(board):
    print(f'\n {board[0]} | {board[1]} | {board[2]}')
    print('---+---+---')
    print(f' {board[3]} | {board[4]} | {board[5]}')
    print('---+---+---')
    print(f' {board[6]} | {board[7]} | {board[8]}\n')

display_board(board)

# update the board with their marker ("X" or "O") and basic input validation.
def place_marker(board, marker, position):
    board[position - 1 ] = marker

def player_choice(board, player_marker):
    while True :
        try:
            position = int(input(f"Player {player_marker}, choose your next position (1-9): "))
            if 1 <= position <= 9 and board[position - 1 ] not in ["X", "O"] :
                return position
            else :
                print("Invalid input or position already taken. Please choose an empty number between 1-9 :")
        except ValueError:
            print("Invalid input. Please enter a number.")

current_board = create_board()
print("Board before a move:")
display_board(current_board)

# check if a player has won after each move.
# involves checking all possible winning combinations (columns, rows and diagonals)
def check_win(board, marker):
    # check rows
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] == marker:
            return True
    # check columns
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] == marker:
            return True
    # check diagonals
    if  (board[0] == board[4] == board[8] == marker ) or \
        (board[2] == board[4] == board[6] == marker):
        return True
    return False

def check_tie(board):
    for spot in board:
        if spot not in ['X', 'O'] :
            return False
    return True


# into the main game loopfunction.
# manage turns, display the board, get player input, check for win or ties and restart game

def play_game() :
    while True:
        board = create_board()
        player1_marker, player2_marker = "X", "O"
        turn = "player 1"
        game_on = True

        print(" Welcome to Tic Tac Toe !!!")

        while game_on:
            if turn == 'Player 1' :
                display_board(board)
                position = player_choice(board, player1_marker)
                place_marker(board, player1_marker, position)

                if check_win(board, player1_marker) :
                    display_board(board)
                    print(f'Congratulation! {turn} ({player1_marker}) has won!')
                    game_on = False
                elif check_tie(board) :
                    display_board(board)
                    print("The game is tie !!")
                    game_on = False
                else :
                    turn = 'Player 2'
            else : # player2's turn
                display_board(board)
                position = player_choice(board, player2_marker)
                place_marker(board, player2_marker, position)

                if check_win(board, player2_marker) :
                    display_board(board)
                    print(f'Congratulation! {turn} ({player2_marker}) has won!')
                    game_on = False
                elif check_tie(board) :
                    display_board(board)
                    print("The game is tie !!")
                    game_on = False
                else :
                    turn =  'Player 1'

        if not input("Play again? (yes/no): ").lower().startswith("y") :
            break

print("Ready to play! Run the 'play_game()' function below to start.")

play_game()
