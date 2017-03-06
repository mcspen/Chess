
class Piece:

    def __init__(self, piece_type, color, symbol, location):
        self.type = piece_type
        self.color = color
        self.symbol = symbol
        self.location = location
        self.initial = True

    def get_moves(self):
        if self.type == 'pawn':
            if self.initial:
                return [(0, 1), (0, 2), (-1, 1), (1, 1)]
            else:
                return [(0, 1), (-1, 1), (1, 1)]
        elif self.type == 'rook':
            moves = []
            for x in range(-7, 8):
                if x == 0:
                    continue
                moves.append((x, 0))
            for y in range(-7, 8):
                if y == 0:
                    continue
                moves.append((0, y))
            return moves
        elif self.type == 'knight':
            return [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        elif self.type == 'bishop':
            moves = []
            for x in range(-7, 8):
                if x == 0:
                    continue
                for y in range(-1, 2):
                    if y == 0:
                        continue
                    moves.append((x,x*y))
            return moves
        elif self.type == 'queen':
            moves = []
            for x in range(-7, 8):
                if x == 0:
                    continue
                moves.append((x, 0))
            for y in range(-7, 8):
                if y == 0:
                    continue
                moves.append((0, y))
            for x in range(-7, 8):
                if x == 0:
                    continue
                for y in range(-1, 2):
                    if y == 0:
                        continue
                    moves.append((x,x*y))
            return moves
        elif self.type == 'king':
            return [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        else:
            return []
