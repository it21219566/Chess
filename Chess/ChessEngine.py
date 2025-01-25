"""
responsible for storing all the information on the current state of the chess game,
responsible for determining valid moves in the current state,
responsible for keeping a move log.
"""

class GameState():
    def __init__(self):
        #the chess board with pieces as an 8*8 2d array
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'K': self.get_king_moves, 'Q': self.get_queen_moves}
        self.whiteToMove = True
        self.moveLog = []
    '''
    takes a move as a parameter and executes it
    does not works for castling, en-passant and pawn promotion
    '''
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.moveLog.append(move) #log the move into the moveLog
        self.whiteToMove = not self.whiteToMove #swap players turn

    '''
    undo the last move
    '''
    def undo_move(self):
        if len(self.moveLog) != 0: #check if there is a move to undo
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove # after undoing the move swap players turn

    ''''
    all moves considering checks
    '''
    def get_valid_moves(self):
        return self.get_possible_moves()

    '''
    all moves without considering checks
    '''
    def get_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves) #calls the appropriate move_function based on piece type
        return moves

    '''
    get all the pawn moves for pawn located in a row, col and add those moves to the list
    '''
    def get_pawn_moves(self, r, c, moves):
        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == '--': #1 square pawn move
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == '--': #2 square pawn move
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == 'b': #if there is an opponents piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: #captures to the right
                if self.board[r-1][c+1][0] == 'b': #if there is an opponents piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else: #black pawn moves
            pass

    '''
    get all the rook moves for pawn located in a row, col and add those moves to the list
    '''
    def get_rook_moves(self, r, c, moves):
        pass

    '''
    get all the bishop moves for pawn located in a row, col and add those moves to the list
    '''
    def get_bishop_moves(self, r, c, moves):
        pass

    '''
    get all the knight moves for pawn located in a row, col and add those moves to the list
    '''
    def get_knight_moves(self, r, c, moves):
        pass

    '''
    get all the king moves for pawn located in a row, col and add those moves to the list
    '''
    def get_king_moves(self, r, c, moves):
        pass

    '''
    get all the queen moves for pawn located in a row, col and add those moves to the list
    '''
    def get_queen_moves(self, r, c, moves):
        pass


class Move():
    #turn rows and columns into ranks and files to make chess notation
    #maps keys to values
    #keys : values
    ranks_to_rows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rows_to_ranks = {v:k for k,v in ranks_to_rows.items()}
    files_to_cols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7,}
    cols_to_files = {v:k for k,v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col #gives a unique id to each move

    '''
    overriding equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False


    def get_chess_notation(self):
        #can add to make this like real chess notation
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c], self.rows_to_ranks[r]