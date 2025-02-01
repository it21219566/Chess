"""
responsible for storing all the information on the current state of the chess game,
responsible for determining valid moves in the current state,
responsible for keeping a move log.
"""
from os import remove


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
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []


    '''
    takes a move as a parameter and executes it
    does not works for castling, en-passant and pawn promotion
    '''
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.moveLog.append(move) #log the move into the moveLog
        self.whiteToMove = not self.whiteToMove #swap players turn
        #update king location
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

    '''
    undo the last move
    '''
    def undo_move(self):
        if len(self.moveLog) != 0: #check if there is a move to undo
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove # after undoing the move swap players turn
            # update king location
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)

    ''''
    all moves considering checks
    '''
    def get_valid_moves(self):
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.whiteToMove:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1: #checked by only 1 piece, block the check or move the king
                moves = self.get_possible_moves()
                # to block the check
                check = self.checks[0] #check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col] #the opponents piece checking the king
                valid_squares = [] #squares that piece can move
                #if knight, must capture the knight or move king, other pieces can be blocked
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i) #check[2] & check[3] are check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col: #once u get the piece and the checks
                            break
                #get rid of any move that does not block the check or move the king
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != 'K': #move does not move the king so it must block or capture the piece
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares: #move does not block the check or capture the piece
                            moves.remove(moves[i])
            else: #double check king has to move
                self.get_king_moves(king_row, king_col, moves)
        else: #not in check so all moves are valid
            moves = self.get_possible_moves()

        return moves

    '''
    all moves without considering checks
    '''
    def get_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves) #calls the appropriate move_function based on piece type
        return moves

    '''
    get all the pawn moves for pawn located in a row, col and add those moves to the list
    '''
    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == '--': #1 square pawn move
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == '--': #2 square pawn move
                        moves.append(Move((r, c), (r-2, c), self.board))
            #captures
            if c-1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == 'b': #if there is an opponents piece to capture
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: #captures to the right
                if self.board[r-1][c+1][0] == 'b': #if there is an opponents piece to capture
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r-1, c+1), self.board))

        else:  # Black pawn moves
            if self.board[r + 1][c] == '--':  # 1 square pawn move
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == '--':  # 2 square pawn move
                        moves.append(Move((r, c), (r + 2, c), self.board))
            #captures
            if c - 1 >= 0:  # Captures to the left
                if self.board[r + 1][c - 1][0] == 'w':  # If there is an opponent's piece to capture
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:  # Captures to the right
                if self.board[r + 1][c + 1][0] == 'w':  # If there is an opponent's piece to capture
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))

    '''
    get all the rook moves for pawn located in a row, col and add those moves to the list
    '''
    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #can not remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins,remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up, down, left and right
        opponent_colour = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board[0]): #within the board
                    if not piece_pinned or pin_direction == d or directions == (-d[0], d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": #valid empty space
                            moves.append(Move((r, c),(end_row, end_col), self.board))
                        elif end_piece[0] == opponent_colour: #opponents piece valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else: #friendly piece invalid
                            break
                else: #off the board
                    break

    '''
    get all the bishop moves for pawn located in a row, col and add those moves to the list
    '''
    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins,remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #4 diagonals
        opponent_colour = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board[0]): #within the board
                    if not piece_pinned or pin_direction == d or directions == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": #valid empty space
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == opponent_colour: #opponents piece valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else: #friendly piece invalid
                            break
                else: #off the board
                    break

    '''
    get all the knight moves for pawn located in a row, col and add those moves to the list
    '''
    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins,remove(self.pins[i])
                break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allay_colour = "w" if self.whiteToMove else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board[0]):
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != allay_colour:  # not an allay piece (an opponents piece or empty)
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    '''
    get all the king moves for pawn located in a row, col and add those moves to the list
    '''
    def get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allay_colour = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 < end_row < len(self.board) and 0 < end_col < len(self.board[0]):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != allay_colour:
                    #place king on the square and check for checks
                    if allay_colour == "w":
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    #place king back on original location
                    if allay_colour == "w":
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)

    '''
    get all the queen moves for pawn located in a row, col and add those moves to the list
    '''
    def get_queen_moves(self, r, c, moves):
        #essentially queen move is a combination of rook moves and bishop moves
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    '''
    returns a list of pins and checks if there are any
    '''
    def check_for_pins_and_checks(self):
        pins = [] #squares where the allied pinned piece is & the direction of the pin
        checks = [] #the squares where the opponent is when checking
        in_check = False
        if self.whiteToMove:
            opponent_colour = "b"
            allay_colour = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            opponent_colour = "w"
            allay_colour = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # check outward from the king for pins and checks
        directions = ((-1, 0), (0, -1), (1, -0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board[0]):
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == allay_colour and end_piece[1] != 'K':
                        if possible_pin == ():  # ist allied piece could be pined
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:  # 2nd allied piece so no check or pin possible on this side
                            break
                    elif end_piece[0] == opponent_colour:
                        type = end_piece[1]
                        # 5 possibilities here in this conditional
                        # 1) orthogonally away from the king, checked by a Rook
                        # 2) diagonally away from the king, checked by a bishop
                        # 3) 1 square diagonally away from the king, checked by a pawn
                        # 4) any direction, checked by a Queen
                        # 5) any direction 1 square away (this is for preventing the king moving to a square controlled by the opposite colour king)
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and ((opponent_colour == 'w' and 6 <= j <= 7) or (
                                        opponent_colour == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == ():  # no other piece blocking
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # a piece blocking so pinned
                                pins.append(possible_pin)
                                break
                        else:  # opponent piece not applying checks
                            break
                else:
                    break  # off board
        # knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board[0]):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == opponent_colour and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks


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