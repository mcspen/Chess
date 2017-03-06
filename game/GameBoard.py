import copy
import json
import sys
from piece import Piece
from text_colors import TextColors

blank_color = "purple"
dark_piece_color = "black"
light_piece_color = "white"
colors = [light_piece_color, dark_piece_color]


class GameBoard:

    # Create board and set pieces
    def __init__(self):
        self.game_board = []
        self.history = []

        for x in range(64):
            temp = Piece('blank', blank_color, ' ', x)
            self.game_board.append(temp)

        # Set pawns
        for x in range(8):
            self.game_board[x+(1*8)] = Piece('pawn', dark_piece_color, 'P', x + (1 * 8))
        for x in range(8):
            self.game_board[x+(6*8)] = Piece('pawn', light_piece_color, 'P', x + (6 * 8))

        # Set rest of pieces
        self.game_board[0] = Piece('rook', dark_piece_color, 'R', 0)
        self.game_board[7] = Piece('rook', dark_piece_color, 'R', 7)
        self.game_board[0+(7*8)] = Piece('rook', light_piece_color, 'R', 0 + (7 * 8))
        self.game_board[7+(7*8)] = Piece('rook', light_piece_color, 'R', 7 + (7 * 8))
        self.game_board[1] = Piece('knight', dark_piece_color, 'N', 1)
        self.game_board[6] = Piece('knight', dark_piece_color, 'N', 6)
        self.game_board[1+(7*8)] = Piece('knight', light_piece_color, 'N', 1 + (7 * 8))
        self.game_board[6+(7*8)] = Piece('knight', light_piece_color, 'N', 6 + (7 * 8))
        self.game_board[2] = Piece('bishop', dark_piece_color, 'B', 2)
        self.game_board[5] = Piece('bishop', dark_piece_color, 'B', 5)
        self.game_board[2+(7*8)] = Piece('bishop', light_piece_color, 'B', 2 + (7 * 8))
        self.game_board[5+(7*8)] = Piece('bishop', light_piece_color, 'B', 5 + (7 * 8))
        self.game_board[4] = Piece('king', dark_piece_color, 'K', 4)
        self.game_board[3] = Piece('queen', dark_piece_color, 'Q', 3)
        self.game_board[4+(7*8)] = Piece('king', light_piece_color, 'K', 4 + (7 * 8))
        self.game_board[3+(7*8)] = Piece('queen', light_piece_color, 'Q', 3 + (7 * 8))

    # Print out the game board and pieces
    def print_board(self):
        color_list = {
            "blue": TextColors.blue,
            "green": TextColors.green,
            "purple": TextColors.purple,
            dark_piece_color: TextColors.orange,
            light_piece_color: TextColors.yellow
        }

        # Print column letters
        print '   a  b  c  d  e  f  g  h'

        # Iterate through rows
        for y in range(8):
            # Print row numbers
            sys.stdout.write(str(8-y) + ' ')

            # Iterate through columns
            for x in range(8):
                square_color = TextColors.blue
                if(x+y) % 2 == 1:
                    square_color = TextColors.purple
                piece = self.game_board[x+(8*y)]
                sys.stdout.write('%s[%s%s%s]%s' % (square_color,
                                                   color_list[piece.color],
                                                   piece.symbol,
                                                   square_color,
                                                   TextColors.end))
            # Print row numbers
            sys.stdout.write(' ' + str(8-y))
            print ''
        # Print column letters
        print '   a  b  c  d  e  f  g  h'

    # Check for clear path
    def is_clear_path(self, x_prev, y_prev, x_new, y_new):
        clear = True

        # If knight, return true
        if self.game_board[x_prev+(8*y_prev)].type == 'knight':
            return clear

        x_cur = x_prev
        y_cur = y_prev

        if x_new - x_prev < 0:
            x_increment = -1
        elif x_new - x_prev > 0:
            x_increment = 1
        else:
            x_increment = 0
        if y_new - y_prev < 0:
            y_increment = -1
        elif y_new - y_prev > 0:
            y_increment = 1
        else:
            y_increment = 0

        x_cur += x_increment
        y_cur += y_increment

        while x_cur != x_new or y_cur != y_new:
            if self.game_board[x_cur+(8*y_cur)].type != 'blank':
                clear = False
                break
            else:
                x_cur += x_increment
                y_cur += y_increment

        return clear

    def is_checked(self, color):
        is_checked = False

        opp_color = colors[(colors.index(color) + 1) % 2]
        opp_moves = self.get_valid_moves(opp_color, False)

        # Get your king location
        king_location = -1
        for piece in self.game_board:
            if piece.color == color and piece.type == "king":
                king_location = piece.location
                break

        # Check if opponent is able to attack king and create list
        for opp_move in opp_moves:
            if opp_move[1] == king_location:
                is_checked = True
                break

        return is_checked

    def get_valid_moves(self, color, check_check=True):
        # Make list of all possible moves
        all_moves = []

        # Iterate through all pieces
        for piece in self.game_board:
            # Only check pieces of the specified color
            if piece.color != color:
                continue

            # Get potentially possible moves
            possible_moves = piece.get_moves()

            # Translate moves into location list
            x = piece.location % 8
            y = piece.location / 8
            move_locations = []
            move_direction = 1
            if color == light_piece_color:
                move_direction = -1
            for possible_move in possible_moves:
                new_x = x + (move_direction * possible_move[0])
                new_y = y + (move_direction * possible_move[-1])
                move_location = new_x + new_y * 8
                # Check that move is in bounds, does not attack own piece, and has a clear path
                if -1 < new_x < 8 \
                        and -1 < new_y < 8 \
                        and self.game_board[move_location].color != piece.color \
                        and (self.is_clear_path(x, y, new_x, new_y) or piece.type == "knight"):
                    move_locations.append(move_location)

                    # Special pawn checks
                    if piece.type == "pawn":
                        if (x != new_x and self.game_board[move_location].type == "blank") \
                                or (x == new_x and self.game_board[move_location].type != "blank") \
                                or (possible_move[1] > 1 and not piece.initial):
                            move_locations.remove(move_location)
            # Add piece's moves to all moves list
            for move in move_locations:
                all_moves.append((piece.location, move))

        # Only allow moves that block check moves, if under check
        if check_check:
            invalid_moves = []
            # Check if still checked after each move
            for move in all_moves:
                temp_board = copy.deepcopy(self)
                temp_board.move_wrapper(move[0], move[1], False)
                # If still checked after move, remove move as a possibility
                if temp_board.is_checked(color):
                    invalid_moves.append(move)
            # Remove invalid moves
            for move in invalid_moves:
                all_moves.remove(move)

        return all_moves

    def move_wrapper(self, old_location, new_location, save=True):

        # Lazy game ending
        if old_location is None or new_location is None:
            return

        color = self.game_board[old_location].color

        x_old = old_location % 8
        y_old = old_location / 8
        x_new = new_location % 8
        y_new = new_location / 8

        self.move(color, x_old, y_old, x_new, y_new, save)

    def move(self, color, x_prev, y_prev, x_new, y_new, save=True):

        piece = self.game_board[x_prev+(8*y_prev)]

        if x_prev < 0 or \
           x_prev > 8 or \
           y_prev < 0 or \
           y_prev > 8 or \
           x_new < 0 or \
           x_new > 8 or \
           y_new < 0 or \
           y_new > 8:
            print 'Coordinates are off the board!'
            return False

        elif piece.type == 'blank':
            print 'There is no piece there!'
            return False

        elif piece.color != color:
            print 'That is not your piece!'
            return False

        # Check if attacking own piece
        elif piece.color == self.game_board[x_new + (8 * y_new)].color:
            print 'You cannot attack your own piece!'
            return False

        color_direction = 1
        if color == light_piece_color:
            color_direction = -1

        # Check if the move is possibly valid for the piece
        possible_moves = piece.get_moves()
        move_x_delta = x_new - x_prev
        move_y_delta = color_direction * (y_new - y_prev)
        if (move_x_delta, move_y_delta) not in possible_moves:
            print 'Not a valid move for a %s!' % piece.type
            return False

        # Check if path is clear
        if piece.type != 'knight':
            if not self.is_clear_path(x_prev, y_prev, x_new, y_new):
                print 'Path is not clear!'
                return False

        # Special pawn checks
        if piece.type == 'pawn':
            if move_x_delta != 0 and self.game_board[x_new+(8*y_new)].color == blank_color:
                print 'A pawn cannot move diagonally!'
                return False
            if move_x_delta == 0 and self.game_board[x_new+(8*y_new)].color != blank_color:
                print 'A pawn can only attack diagonally!'
                return False
            # Change pawn to new piece
            if y_new == 0 or y_new == 7:
                # Change to queen for now
                self.game_board[x_prev + (8 * y_prev)] = Piece('queen', piece.color, 'Q', x_prev + (8 * y_prev))
                piece = self.game_board[x_prev + (8 * y_prev)]

        # Set initial position to false
        if piece.initial:
            piece.initial = False

        # Move piece
        self.game_board[x_new + (8 * y_new)] = self.game_board[x_prev + (8 * y_prev)]
        self.game_board[x_prev + (8 * y_prev)] = Piece('blank', "purple", ' ', x_prev + (8 * y_prev))
        piece.location = x_new + (8 * y_new)

        # Save game
        if save:
            self.history.append((color, x_prev + (8 * y_prev), piece.location))
            self.save_game()

        # Check for check and checkmate

        return True

    def save_game(self):
        save_data = {"history": self.history}

        with open('saved_game.json', 'w') as saved_game_file:
            json.dump(save_data, saved_game_file)
            saved_game_file.close()

    def load_game(self):
        save_data = {}
        with open('saved_game.json', 'r') as saved_game_file:
            save_data = json.load(saved_game_file)
            saved_game_file.close()

        # Convert saved JSON data back into game board
        self.__init__()
        for move in save_data["history"]:
            self.move_wrapper(move[1], move[2])
