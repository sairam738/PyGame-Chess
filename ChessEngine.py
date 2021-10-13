class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.white_to_move = True
        self.move_log = []
        self.move_function = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                              'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.check_mate = False
        self.stale_mate = False
        self.enPassantMove = ()
        self.enpassant_possible_log = [self.enPassantMove]
        self.currCastlingRights = castlingRights(True, True, True, True)
        self.castlingRightsLog = [castlingRights(self.currCastlingRights.wks, self.currCastlingRights.bks,
                                                 self.currCastlingRights.wqs, self.currCastlingRights.bqs)]

    def make_move(self, move):
        #print(move.startrow, move.startcol, move.endrow, move.endcol)
        self.board[move.startrow][move.startcol] = "--"
        self.board[move.endrow][move.endcol] = move.pieceMoved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

        if move.pieceMoved == 'wK':
            self.white_king_pos = (move.endrow, move.endcol)
        elif move.pieceMoved == 'bK':
            self.black_king_pos = (move.endrow, move.endcol)

        if move.is_pawn_promotion:
            self.board[move.endrow][move.endcol] = move.pieceMoved[0] + move.promotion_choice

        if move.is_en_passant_move:
            self.board[move.startrow][move.endcol] = "--"

        if move.is_castling_move:
            if move.endcol - move.startcol == 2:
                self.board[move.startrow][move.endcol - 1] = self.board[move.startrow][move.endcol + 1]
                self.board[move.startrow][move.endcol + 1] = '--'
            else:
                self.board[move.startrow][move.endcol + 1] = self.board[move.startrow][move.endcol - 2]
                self.board[move.startrow][move.endcol - 2] = '--'

        if move.pieceMoved[1] == 'p' and abs(move.endrow - move.startrow) == 2:
            self.enPassantMove = ((move.startrow + move.endrow) // 2, move.startcol)
        else:
            self.enPassantMove = ()
        self.enpassant_possible_log.append(self.enPassantMove)

        self.update_castling_rights(move)
        self.castlingRightsLog.append(castlingRights(self.currCastlingRights.wks, self.currCastlingRights.bks,
                                                     self.currCastlingRights.wqs, self.currCastlingRights.bqs))

    def update_castling_rights(self, move):
        if move.pieceMoved == 'wK':
            self.currCastlingRights.wks = False
            self.currCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currCastlingRights.bqs = False
            self.currCastlingRights.bks = False
        if move.pieceMoved == 'wR':
            if move.startcol == 7:
                self.currCastlingRights.wks = False
            elif move.startcol == 0:
                self.currCastlingRights.wqs = False
        elif move.pieceMoved == 'bR':
            if move.startcol == 7:
                self.currCastlingRights.bks = False
            elif move.startcol == 0:
                self.currCastlingRights.bqs = False

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            #print(move.startrow, move.startcol, move.endrow, move.endcol)
            self.board[move.endrow][move.endcol] = move.pieceKilled
            self.board[move.startrow][move.startcol] = move.pieceMoved
            self.white_to_move = not self.white_to_move
            if move.pieceMoved == 'wK':
                self.white_king_pos = (move.startrow, move.startcol)
            elif move.pieceMoved == 'bK':
                self.black_king_pos = (move.startrow, move.startcol)

            if move.is_en_passant_move:
                self.board[move.endrow][move.endcol] = "--"
                self.board[move.startrow][move.endcol] = move.pieceKilled
            if move.is_castling_move:
                if move.endcol - move.startcol == 2:
                    self.board[move.startrow][move.endcol + 1] = self.board[move.startrow][move.endcol - 1]
                    self.board[move.startrow][move.endcol - 1] = '--'
                else:
                    self.board[move.startrow][move.endcol - 2] = self.board[move.startrow][move.endcol + 1]
                    self.board[move.startrow][move.endcol + 1] = '--'
            self.enpassant_possible_log.pop()
            self.enPassantMove = self.enpassant_possible_log[-1]
            self.castlingRightsLog.pop()
            newrights = self.castlingRightsLog[-1]
            self.currCastlingRights = castlingRights(newrights.wks, newrights.bks, newrights.wqs, newrights.bqs)

    def get_valid_moves(self):
        tempEnpassant = self.enPassantMove
        temp_castle_rights = castlingRights(self.currCastlingRights.wks, self.currCastlingRights.bks,
                                            self.currCastlingRights.wqs, self.currCastlingRights.bqs)
        # 1) Generate all the possible moves
        moves = self.get_all_possible_moves()
        if self.white_to_move:
            self.get_castling_moves(self.white_king_pos[0], self.white_king_pos[1], moves)
        else:
            self.get_castling_moves(self.black_king_pos[0], self.black_king_pos[1], moves)
        # 2) For Each Move Make the move
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])

            # 3) Generate all opponent moves
            # 4) For each opponent move, see if they attack your king
            # 5) If the king is attacked remove that move
            if self.in_check():
                moves.remove(moves[i])
            self.undo_move()

        if len(moves) == 0:
            if self.in_check():
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.check_mate = False
            self.stale_mate = False

        self.enPassantMove = tempEnpassant
        self.currCastlingRights = temp_castle_rights

        print(len(moves))
        return moves

    def in_check(self):
        if self.white_to_move:
            return self.square_index_attack(self.black_king_pos[0], self.black_king_pos[1])
        else:
            return self.square_index_attack(self.white_king_pos[0], self.white_king_pos[1])

    def square_index_attack(self, r, c):
        opp_moves = self.get_all_possible_moves()
        for move in opp_moves:
            if move.endrow == r and move.endcol == c:
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_function[piece](r, c, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':
                    moves.append(Move((r, c), (r - 2, c), self.board))

            if c - 1 >= 0 and self.board[r - 1][c - 1][0] == 'b':
                moves.append(Move((r, c), (r - 1, c - 1), self.board))
            elif c - 1 >= 0 and (r - 1, c - 1) == self.enPassantMove:
                moves.append(Move((r, c), (r - 1, c - 1), self.board, enpassant_move=True))

            if c + 1 <= 7 and self.board[r - 1][c + 1][0] == 'b':
                moves.append(Move((r, c), (r - 1, c + 1), self.board))
            elif c + 1 <= 7 and (r - 1, c + 1) == self.enPassantMove:
                moves.append(Move((r, c), (r - 1, c + 1), self.board, enpassant_move=True))

        if not self.white_to_move:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == '--':
                    moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0 and self.board[r + 1][c - 1][0] == 'w':
                moves.append(Move((r, c), (r + 1, c - 1), self.board))
            elif c - 1 >= 0 and (r + 1, c - 1) == self.enPassantMove:
                moves.append(Move((r, c), (r + 1, c - 1), self.board, enpassant_move=True))

            if c + 1 <= 7 and self.board[r + 1][c + 1][0] == 'w':
                moves.append(Move((r, c), (r + 1, c + 1), self.board))
            elif c + 1 <= 7 and (r + 1, c + 1) == self.enPassantMove:
                moves.append(Move((r, c), (r + 1, c + 1), self.board, enpassant_move=True))

    def get_rook_moves(self, r, c, moves):
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        enemy = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if self.board[end_row][end_col] == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif self.board[end_row][end_col][0] == enemy:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_bishop_moves(self, r, c, moves):
        directions = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        enemy = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if self.board[end_row][end_col] == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif self.board[end_row][end_col][0] == enemy:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_knight_moves(self, r, c, moves):
        directions = [(2, -1), (2, 1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        ally = 'w' if self.white_to_move else 'b'
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if self.board[end_row][end_col][0] != ally:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_queen_moves(self, r, c, moves):
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (1, 1), (-1, 1)]
        enemy = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if self.board[end_row][end_col] == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif self.board[end_row][end_col][0] == enemy:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_king_moves(self, r, c, moves):
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (1, 1), (-1, 1)]
        enemy = 'b' if self.white_to_move else 'w'
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if self.board[end_row][end_col] == "--":
                    moves.append(Move((r, c), (end_row, end_col), self.board))
                elif self.board[end_row][end_col][0] == enemy:
                    moves.append(Move((r, c), (end_row, end_col), self.board))
            else:
                continue

    def get_castling_moves(self, r, c, moves):
        if self.in_check():
            return
        if (self.white_to_move and self.currCastlingRights.wks) or \
                (not self.white_to_move and self.currCastlingRights.bks):
            self.get_king_side_castling_moves(r, c, moves)
        if (self.white_to_move and self.currCastlingRights.wqs) or \
                (not self.white_to_move and self.currCastlingRights.bqs):
            self.get_queen_side_castling_moves(r, c, moves)

    def get_king_side_castling_moves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            self.white_to_move = not self.white_to_move
            if not self.square_index_attack(r, c + 1) and not self.square_index_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, castling_move=True))
            self.white_to_move = not self.white_to_move

    def get_queen_side_castling_moves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            self.white_to_move = not self.white_to_move
            if not self.square_index_attack(r, c - 1) and not self.square_index_attack(r, c - 2) \
                    and not self.square_index_attack(r, c - 3):
                moves.append(Move((r, c), (r, c - 2), self.board, castling_move=True))
            self.white_to_move = not self.white_to_move


class castlingRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    Cols_to_files = {0: "1", 1: "2", 2: "3", 3: "4", 4: "5", 5: "6", 6: "7", 7: "8"}
    Rows_to_files = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}

    def __init__(self, start_square, end_square, board, enpassant_move=False, castling_move=False):
        self.startrow = start_square[0]
        self.startcol = start_square[1]
        self.endrow = end_square[0]
        self.endcol = end_square[1]
        self.pieceMoved = board[self.startrow][self.startcol]
        self.pieceKilled = board[self.endrow][self.endcol]
        self.is_pawn_promotion = False
        self.promotion_choice = 'Q'
        # Pawn Promotion
        if (self.pieceMoved == "wp" and self.endrow == 0) or (self.pieceMoved == 'bp' and self.endrow == 7):
            self.is_pawn_promotion = True

        # En Passant Move
        self.is_en_passant_move = enpassant_move
        self.is_castling_move = castling_move
        if self.is_en_passant_move:
            self.pieceKilled = "wp" if self.pieceMoved == "bp" else "bp"
        self.moveID = self.startrow * 1000 + self.startcol * 100 + self.endrow * 10 + self.endcol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_notation(self):
        return (chr(97 + self.startcol)) + (chr(56 - self.startrow)) + (chr(97 + self.endcol)) + (chr(56 - self.endrow))

