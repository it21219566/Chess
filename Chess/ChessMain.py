"""
main driver file
responsible for handling user inputs and displaying the current GameState objects.
"""
import pygame as p
from Chess import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''
Initiate the images
'''
def load_images():
    pieces = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wP', 'bR', 'bN', 'bB', 'bQ', 'bK', 'bP']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

'''
the main function
responsible for handling user inputs and graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    load_images() # executed once before the while loop
    running = True
    sq_selected = () #if no square is selected, keep track of the last click of the user
    player_clicks = [] #keep track of player clicks
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #location of the mouse as x & y
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sq_selected == (row, col): #if the player clicks the same square twice
                    sq_selected = () #deselect
                    player_clicks = [] #clear player clicks
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected) #append for both 1st & last clicks
                if len(player_clicks) == 2: #after 2nd click
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                    print(move.get_chess_notation())
                    gs.make_move(move)
                    sq_selected = () #after making the move resets the user clicks
                    player_clicks = []
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undo_move()

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
responsible for all the graphics on the current gameState
'''
def draw_game_state(screen, gs):
    draw_board(screen)
    draw_pieces(screen, gs.board)

'''
order of drawing 01
responsible for drawing the squares in the board
'''
def draw_board(screen):
    colours = [p.Color("white"), p.Color("light blue")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            colour = colours[((r+c) % 2)]
            p.draw.rect(screen, colour, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

''''
order of drawing 02
responsible for drawing the pieces on the board using current gameState.board
'''
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #if the square is not empty
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == '__main__':
    main()