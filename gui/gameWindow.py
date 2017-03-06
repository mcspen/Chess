from GUI import Button, Font, Geometry, Image, Label, RadioButton, RadioGroup, View, Window
from GUI.StdFonts import system_font
from colors import *
from game.GameBoard import GameBoard
from ai.AI import AI
from multiprocessing import Pipe, Process

win_width = 500
win_height = 500
board_offset = 25
board_border = 10
line_width = 2
square_size = (win_width - 2*board_offset - 2*board_border - 7*line_width) / 8

light_piece_color = "white"
dark_piece_color = "black"


def start_ai(game_board, color, first_player, ai_pipe):
    AI(game_board, color, first_player, ai_pipe)


def open_game_window(window_x, window_y):

    pieces_list = []
    buttons_list = []
    game_over = {"status": False}

    # ========== Window ==========
    win_game = Window()
    win_game.title = "Chess Game"
    win_game.auto_position = False
    win_game.position = (window_x, window_y)
    win_game.size = (win_width, win_height)
    win_game.resizable = 0
    win_game.name = "Chess Game"

    # ========== Window Image View ==========
    class ChessBoardImage(View):
        def draw(self, c, r):
            c.backcolor = black
            c.erase_rect(r)

            # Board
            c.forecolor = brown
            c.fill_rect((board_offset, board_offset, win_width - board_offset, win_height - board_offset))

            # Squares
            square_colors = [beige, darkish_brown]
            color_idx = 0
            for x in range(0, 8):
                for y in range(0, 8):
                    square_x0 = board_offset + board_border + x * (square_size + line_width)
                    square_y0 = board_offset + board_border + y * (square_size + line_width)
                    square_x1 = square_x0 + square_size
                    square_y1 = square_y0 + square_size

                    c.forecolor = square_colors[color_idx]
                    c.fill_rect((square_x0, square_y0, square_x1, square_y1))
                    color_idx = (color_idx + 1) % 2
                color_idx = (color_idx + 1) % 2

    view = ChessBoardImage(size=win_game.size)

    # ========== Title ==========
    # title = Label(text="Chess")
    # title.font = Font("Times", 3 * system_font.size, ['bold'])
    # title.width = 300
    # title.height = 50
    # title.x = (win_width - title.width) / 2
    # title.y = 5
    # title.color = white
    # title.just = 'center'
    # piece_list.append(title)

    # Create piece labels
    def create_piece_labels():
        piece_colors = {"white": white, "black": black, "purple": clear}
        for piece in game_board.game_board:
            x = piece.location % 8
            y = piece.location / 8
            square_x0 = board_offset + board_border + x * (square_size + line_width)
            square_y0 = board_offset + board_border + y * (square_size + line_width)

            piece_label = Label(text=piece.symbol,
                                x=square_x0,
                                y=square_y0 + 7,
                                width=square_size,
                                height=square_size,
                                font=Font("Times", 3 * system_font.size, ['bold']),
                                color=piece_colors[piece.color],
                                just='center')
            if len(game_board.history) > 0 and piece.location == game_board.history[-1][2]:
                if game_board.history[-1][0] == "white":
                    piece_label.color = light_red
                else:
                    piece_label.color = dark_red
            pieces_list.append(piece_label)

    # Draw piece buttons on board
    def create_piece_buttons(current_color):
        # If two cpus, make a next button
        if players[0]["player"] == "cpu" and players[1]["player"] == "cpu":
            next_btn_width = 150
            next_btn_height = 25
            next_btn = Button(title="Next AI Move",
                              x=(win_width - next_btn_width) / 2,
                              y=board_offset + board_border + 8 * (square_size + line_width) + 10,
                              width=next_btn_width,
                              height=next_btn_height,
                              font=Font("Times", 2 * system_font.size, []),
                              action=(ai_next_btn_action, players[0]))
            buttons_list.append(next_btn)

        else:
            # Get list of pieces with valid moves
            all_moves = game_board.get_valid_moves(current_color)
            pieces_list = []
            for move in all_moves:
                pieces_list.append(move[0])
            pieces_list = list(set(pieces_list))

            # If no moves, game is over
            if len(pieces_list) < 1:
                end_game()

            # Create button for each piece with valid moves
            for piece_location in pieces_list:
                x = piece_location % 8
                y = piece_location / 8
                square_x0 = board_offset + board_border + x * (square_size + line_width)
                square_y0 = board_offset + board_border + y * (square_size + line_width)

                piece_btn = Button(title=game_board.game_board[piece_location].symbol,
                                   x=square_x0 + square_size/6,
                                   y=square_y0 + square_size/6,
                                   width=square_size*2/3,
                                   height=square_size*2/3,
                                   font=Font("Times", 2 * system_font.size, ['bold']),
                                   action=(get_move, piece_location))
                buttons_list.append(piece_btn)

    # Remove piece buttons and draw move buttons
    def get_move(current_piece_location):
        # Remove piece buttons
        remove_buttons()

        # Create move buttons
        create_move_buttons(current_piece_location)

        # Draw move buttons
        draw_buttons()

    # Draw piece move buttons on board
    def create_move_buttons(current_piece_location):
        # Get current piece based on location
        current_piece = game_board.game_board[current_piece_location]

        # Create cancel (don't move this piece) button
        x = current_piece.location % 8
        y = current_piece.location / 8
        square_x0 = board_offset + board_border + x * (square_size + line_width)
        square_y0 = board_offset + board_border + y * (square_size + line_width)
        cancel_btn = Button(title=current_piece.symbol,
                            x=square_x0 + square_size/6,
                            y=square_y0 + square_size/6,
                            width=square_size*2/3,
                            height=square_size*2/3,
                            font=Font("Times", 2 * system_font.size, ['bold']),
                            action=(cancel_btn_action, current_piece.color))
        buttons_list.append(cancel_btn)

        # Get potentially possible moves
        all_moves = game_board.get_valid_moves(current_piece.color)
        possible_moves = []
        for move in all_moves:
            if move[0] == current_piece.location:
                possible_moves.append(move[1])

        # Create buttons for each of the possible moves
        for move_location in possible_moves:
            x = move_location % 8
            y = move_location / 8
            square_x0 = board_offset + board_border + x * (square_size + line_width)
            square_y0 = board_offset + board_border + y * (square_size + line_width)
            move_btn = Button(title=game_board.game_board[move_location].symbol,
                              x=square_x0 + square_size / 6,
                              y=square_y0 + square_size / 6,
                              width=square_size * 2 / 3,
                              height=square_size * 2 / 3,
                              font=Font("Times", 2 * system_font.size, ['bold']),
                              action=(move_piece, current_piece_location, move_location))
            buttons_list.append(move_btn)

    def move_piece(old_location, new_location):
        # Remove piece buttons
        remove_buttons()
        # Remove piece labels
        remove_labels()

        # Move piece on game board
        game_board.move_wrapper(old_location, new_location)

        # Make it next players turn
        players.reverse()

        # If playing with CPU, make cpu move
        if players[0]["player"] == "cpu":
            ai_move(players[0])

        # Create and draw piece labels
        create_piece_labels()
        draw_labels()

        if not game_over["status"]:
            # Create and draw piece buttons
            create_piece_buttons(players[0]["color"])
            draw_buttons()

    def ai_move(player):
        player["pipe"].send(("update", game_board))
        player["pipe"].send(("move",))
        ai_move_old, ai_move_new = player["pipe"].recv()
        game_board.move_wrapper(ai_move_old, ai_move_new)
        player["pipe"].send(("update", game_board))
        players.reverse()

        # If no move was left, end game
        if ai_move_old is None or ai_move_new is None:
            end_game()

    def ai_next_btn_action(player):
        # Remove piece buttons
        remove_buttons()
        # Remove piece labels
        remove_labels()

        # Make AI's move
        ai_move(player)

        # Create and draw piece labels
        create_piece_labels()
        draw_labels()

        if not game_over["status"]:
            # Create and draw piece buttons
            create_piece_buttons(players[0]["color"])
            draw_buttons()

    def cancel_btn_action(current_color):
        remove_buttons()
        create_piece_buttons(current_color)
        draw_buttons()

    def draw_labels():
        for item in pieces_list:
            view.add(item)

    def draw_buttons():
        for item in buttons_list:
            view.add(item)

    # Remove labels
    def remove_labels():
        for item in pieces_list:
            view.remove(item)
        del pieces_list[:]

    # Remove buttons
    def remove_buttons():
        for item in buttons_list:
            view.remove(item)
        del buttons_list[:]

    def end_game():
        if players[0]["player"] == "cpu":
            players[0]["pipe"].send("terminate")
            players[0]["ai process"].terminate()
        if players[1]["player"] == "cpu":
            players[1]["pipe"].send("terminate")
            players[1]["ai process"].terminate()
        remove_buttons()
        game_over["status"] = True

    # Initialize Game
    game_board = GameBoard()
    #game_board.load_game()

    # Assign players and create AI if it is cpu
    white_player = "cpu"
    black_player = "human"

    if white_player == "cpu":
        ai_pipe_white, controller_pipe_white = Pipe()
        ai_process_white = Process(target=start_ai, args=(game_board, "white", "white", ai_pipe_white))
        ai_process_white.start()
        white_player = {"color": "white",
                        "player": "cpu",
                        "pipe": controller_pipe_white,
                        "ai process": ai_process_white}
    else:
        white_player = {"color": "white",
                        "player": "human"}
    if black_player == "cpu":
        ai_pipe_black, controller_pipe_black = Pipe()
        ai_process_black = Process(target=start_ai, args=(game_board, "black", "white", ai_pipe_black))
        ai_process_black.start()
        black_player = {"color": "black",
                        "player": "cpu",
                        "pipe": controller_pipe_black,
                        "ai process": ai_process_black}
    else:
        black_player = {"color": "black",
                        "player": "human"}

    players = [white_player, black_player]

    if players[0]["player"] == "cpu" and players[1]["player"] == "human":
        ai_move(players[0])

    # ========== Add components to view and add view to window ==========
    create_piece_labels()
    draw_labels()
    create_piece_buttons(players[0]["color"])
    draw_buttons()

    win_game.add(view)
    view.become_target()
    win_game.show()
