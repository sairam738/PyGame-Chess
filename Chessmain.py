import pygame as p
from stockfish import Stockfish

import ChessEngine

width = height = 512
dimension = 8
sq_size = width // dimension

images = {}
whiteMove = True;

stfish = Stockfish("stockfish_14_win_x64_avx2/stockfish_14_x64_avx2.exe")

stfish.set_position([])

def loadImages():
    pieces = ["bB", "bK", "bN", "bp", "bQ", "bR", "wB", "wK", "wN", "wp", "wQ", "wR"]
    for piece in pieces:
        images[piece] = p.image.load("images/" + piece + ".png")


def draw_game_state(screen, gs):
    drawBoard(screen)
    drawPiece(screen,gs.board)

def drawBoard(screen):
    colors = [p.Color("gray"), p.Color("brown")]
    for i in range(8):
        for j in range(8):
            p.draw.rect(screen, colors[(i + j) % 2], (j * sq_size, i * sq_size, sq_size, sq_size))


def drawPiece(screen, board):
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece != "--":
                screen.blit(images[board[i][j]], p.Rect(j * sq_size, i * sq_size, sq_size, sq_size))

def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    gs = ChessEngine.GameState()
    move_made = False
    valid_moves = gs.get_valid_moves()
    screen.fill(p.Color("white"))
    loadImages()
    running = True
    clicks = []
    sq_selected = ()
    while running:

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // sq_size
                row = location[1] // sq_size
                if sq_selected == (row, col):
                    sq_selected = ()
                    clicks = []
                else:
                    sq_selected = (row, col)
                    clicks.append(sq_selected)
                if len(clicks) == 2:
                    move = ChessEngine.Move(clicks[0],clicks[1],gs.board)
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i] :

                            gs.make_move(valid_moves[i])
                            #gs.make_move()
                            #stock fish after moving

                            stfish.make_moves_from_current_position([valid_moves[i].get_chess_notation()])
                            blackMove = stfish.get_best_move()
                            print(blackMove)
                            stfish.make_moves_from_current_position([blackMove])
                            stPos = (ord('8') - ord(blackMove[1]), ord(blackMove[0]) - ord('a'))
                            enPos = (ord('8') - ord(blackMove[3]), ord(blackMove[2]) - ord('a'))
                            print(stPos, enPos)
                            CompMove = ChessEngine.Move(stPos, enPos, gs.board)
                            gs.make_move(CompMove)


                            move_made = True
                            clicks = []
                            sq_selected = ()
                    if not move_made:
                        clicks = [sq_selected]
            elif e.type ==  p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    gs.undo_move()
                    move_made = True

        if move_made:

            #print(move.get_chess_notation())
            #print(blackMove)
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs)
        clock.tick(25)
        p.display.update()

if __name__ == "__main__":
    main()
