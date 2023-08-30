import os
import sys
import time
import subprocess
from threading import Timer
import logging

import argparse
from dotenv import load_dotenv

import numpy as np

from tkinter import *
from tkinter.ttk import *

load_dotenv()

MAP_EXPORT_FILE = os.environ['MAP_EXPORT_FILE']
STATE_EXPORT_FILE = os.environ['STATE_EXPORT_FILE']

BOARD_SIZE = int(os.environ['BOARD_SIZE'])
BOARD_EDGE = int(os.environ['BOARD_EDGE'])
FRAME_SIZE = BOARD_EDGE * BOARD_SIZE
MARGIN = int(os.environ['MARGIN'])

BASE_FONT = os.environ['BASE_FONT']
SMALL_FONT = ' '.join([BASE_FONT, os.environ['SMALL_FONT_SIZE']])
LARGE_FONT = ' '.join([BASE_FONT, os.environ['LARGE_FONT_SIZE'], 'bold'])
EXTRA_LARGE_FONT = ' '.join([BASE_FONT, os.environ['EXTRA_LARGE_FONT_SIZE'], 'bold'])

TIME_OUT = int(os.environ['TIME_OUT'])
MOVE_EXPORT_FILE = os.environ['MOVE_EXPORT_FILE']

SLEEP_TIME = float(os.environ['SLEEP_TIME'])

WINDOW_SIZE = FRAME_SIZE * BOARD_SIZE + MARGIN * BOARD_SIZE * 2

root = Tk()
root.title('Super tic-tac-toe')
icon = PhotoImage(file='./assets/icon.png')
root.iconphoto(False, icon)
canvas = Canvas(root, bg=os.environ['BACKGROUP_COLOR'], width=WINDOW_SIZE, height=WINDOW_SIZE)

logger = None

def draw_main_board():
    for j in range(1, BOARD_SIZE):
        for i in range(BOARD_SIZE):
            canvas.create_line(MARGIN * j * 2 + FRAME_SIZE * j, MARGIN * (2 * i + 1) + FRAME_SIZE * i,
                            MARGIN * j * 2 + FRAME_SIZE * j, MARGIN * (2 * i + 1) + FRAME_SIZE * (i + 1), fill=os.environ['BORDER_COLOR'])
            
            canvas.create_line(MARGIN * (2 * i + 1) + FRAME_SIZE * i, MARGIN * j * 2 + FRAME_SIZE * j,
                            MARGIN * (2 * i + 1) + FRAME_SIZE * (i + 1),MARGIN * j * 2 + FRAME_SIZE * j, fill=os.environ['BORDER_COLOR'])

def drwa_cell_board(idx):
    y, x = divmod(idx, BOARD_SIZE)
    start_x = MARGIN * (x * 2 + 1) + FRAME_SIZE * x
    start_y = MARGIN * (y * 2 + 1) + FRAME_SIZE * y

    for i in range(1, BOARD_SIZE):
        canvas.create_line(start_x + BOARD_EDGE * i, start_y, 
                   start_x + BOARD_EDGE * i, start_y + FRAME_SIZE, fill=os.environ['CELL_COLOR'])

        canvas.create_line(start_x, start_y + BOARD_EDGE * i, 
                   start_x + FRAME_SIZE, start_y + BOARD_EDGE * i, fill=os.environ['CELL_COLOR'])

class Move:
    def __init__(self, char, value, color):
        self.__text = char
        self.__value = value
        self.__color = color

    @property
    def text(self):
        return self.__text
    
    @property
    def value(self):
        return self.__value
    
    @property
    def color(self):
        return self.__color
    
    @property
    def win_walue(self):
        return self.__value * BOARD_SIZE

X = Move(os.environ['FIRST_PLAYER_CAHR'],
          1,
            os.environ['FIRST_PLAYER_COLOR'])
O = Move(os.environ['SECOND_PLAYER_CHAR']
         , -1,
          os.environ['SECOND_PLAYER_COLOR'])
TIE = 2
NOT_DONE_YET = -2

def check_win(board):
    filled = np.sum(board != 0)
    row_sum = board.sum(axis=1)
    column_sum = board.sum(axis=0)
    main_diagonal_sum = board.trace()
    anti_diagonal_sum = np.rot90(board).trace()

    if X.win_walue in row_sum or \
        X.win_walue in column_sum or \
        main_diagonal_sum == X.win_walue or \
        anti_diagonal_sum == X.win_walue:

        return X.value
    elif O.win_walue in row_sum or \
        O.win_walue in column_sum or \
        main_diagonal_sum == O.win_walue or \
        anti_diagonal_sum == O.win_walue:

        return O.value
    
    elif filled == BOARD_SIZE ** 2:
        return TIE
    else:
        return NOT_DONE_YET

class MiniBoard:
    def __init__(self, board_idx):
        self.__board = np.zeros((BOARD_SIZE, BOARD_SIZE))
        self.__board_y, self.__board_x = divmod(board_idx, BOARD_SIZE)
        self.__board_start_x = MARGIN * (self.__board_x * 2 + 1) + FRAME_SIZE * self.__board_x
        self.__board_start_y = MARGIN * (self.__board_y * 2 + 1) + FRAME_SIZE * self.__board_y
        self.__filled = 0

    def move(self, idx, move):
        self.__filled += 1
        y, x = divmod(idx, BOARD_SIZE)
        self.__board[y, x] = move.value

        cell_y, cell_x = divmod(idx, BOARD_SIZE)

        start_x = self.__board_start_x  + cell_x * BOARD_EDGE + int(BOARD_EDGE * .5)
        start_y = self.__board_start_y + cell_y * BOARD_EDGE + int(BOARD_EDGE * .5)

        canvas.create_text(start_x, start_y, text=move.text, fill=move.color, font=SMALL_FONT)

    def fill_board(self, move):
        cell_y, cell_x = divmod(BOARD_SIZE ** 2 // 2, BOARD_SIZE)

        start_x = MARGIN * (self.__board_x * 2 + 1) + FRAME_SIZE * self.__board_x + cell_x * BOARD_EDGE + int(BOARD_EDGE * .5)
        start_y = MARGIN * (self.__board_y * 2 + 1) + FRAME_SIZE * self.__board_y + cell_y * BOARD_EDGE + int(BOARD_EDGE * .5)

        canvas.create_rectangle(self.__board_start_x, self.__board_start_y,
                                 self.__board_start_x + FRAME_SIZE, self.__board_start_y + FRAME_SIZE, fill=os.environ['BACKGROUP_COLOR'], outline=os.environ['BACKGROUP_COLOR'])
        canvas.create_text(start_x, start_y, text=move.text, fill=move.color, font=LARGE_FONT)

    @property
    def board(self):
        return self.__board
    
    def __str__(self):
        return '\n'.join(' '.join([str(int(i)) for i in row]) for row in self.__board)
                
class Board:
    def __init__(self):
        self.__cells = [MiniBoard(i) for i in range(BOARD_SIZE ** 2)]
        self.__board = np.zeros((BOARD_SIZE, BOARD_SIZE))
        draw_main_board()        
        for i in range(BOARD_SIZE ** 2):
            drwa_cell_board(i)

        self.__available_boards = 2 ** BOARD_SIZE ** 2  - 1
        self.__board_binaies = [self.__available_boards ^ (1 << i) for i in range(BOARD_SIZE ** 2)]
        self.__last_board_idx = -1
        self.__done = NOT_DONE_YET
        self.__filled = 0

        self.__move = X

    def __get_opponent(self):
        if self.__move == X:
            return O
        if self.__move == O:
            return X

    def __swap_turn(self):
        self.__move = self.__get_opponent()

    def __check_win(self, board_idx, win_state, move):
        if win_state == move.value:
            y, x = divmod(board_idx, BOARD_SIZE)
            self.__board[y, x] = win_state
            self.__cells[board_idx].fill_board(move)
            self.__available_boards = self.__available_boards & self.__board_binaies[board_idx]
            self.__filled += 1
            return True
        
        return False
    
    def __announce_win(self, win_state, move):
        if win_state == move.value:
            text_x, text_y = WINDOW_SIZE // 2, WINDOW_SIZE // 2

            self.__done = move.value
            canvas.create_rectangle(0, 0, WINDOW_SIZE, WINDOW_SIZE, fill=os.environ['BACKGROUP_COLOR'], outline=os.environ['BACKGROUP_COLOR'])
            canvas.create_text(text_x, text_y, text=move.text, fill=move.color, font=EXTRA_LARGE_FONT)
    
    def __is_move_valid(self, board_idx, cell_idx):
        y, x = divmod(cell_idx, BOARD_SIZE)
        return board_idx in self.available_boards and self.__cells[board_idx].board[y, x] == 0
    

    def announce_opponents_win(self):
        opponent = self.__get_opponent()
        self.__announce_win(opponent.value, opponent)

    def move(self, board_idx, cell_idx):
        if not self.__is_move_valid(board_idx, cell_idx):
            self.announce_opponents_win()
            return False
        
        self.__cells[board_idx].move(cell_idx, self.__move)
        win_state = check_win(self.__cells[board_idx].board)
        self.__last_board_idx = cell_idx

        time.sleep(SLEEP_TIME)
        root.update()

        self.__check_win(board_idx, win_state, X) or self.__check_win(board_idx, win_state, O)
        board_win_state = check_win(self.__board)
        self.__announce_win(board_win_state, X) or self.__announce_win(board_win_state, O)

        if board_win_state == TIE:
            self.__done = TIE

        self.__swap_turn()
        return True
    
    def print_board(self):
        logger.info(self.__board)

    def __decode_binary(self, binary):
        codes = []
        counter = 0

        while binary > 0:
            if binary % 2 == 1:
                codes.append(counter)

            binary //= 2
            counter += 1

        return codes

    def get_available_moves_for_cell(self, board_idx):
        if self.__available_boards & (1 << board_idx) == 0:
            return []
        
        moves = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.__cells[board_idx].board[i, j] == 0:
                    idx = i * BOARD_SIZE + j
                    moves.append(idx)

        return moves


    @property
    def available_boards(self):
        if self.__last_board_idx == -1:
            moves = self.__available_boards
        else:
            y, x = divmod(self.__last_board_idx, BOARD_SIZE)
            if self.__board[y, x] != 0:
                moves = self.__available_boards
            else:
                moves = 1 << self.__last_board_idx

        return self.__decode_binary(moves)
    
    @property
    def get_available_moves(self):
        moves = []
        for cell in self.available_boards:
            for move in self.get_available_moves_for_cell(cell):
                moves.append((cell, move))

        return moves
    
    @property
    def done(self):
        return self.__done
    
    def __str__(self):
        board = []

        for i in range(BOARD_SIZE ** 2):
            row = []
            for j in range(BOARD_SIZE ** 2):
                cell_x, cell_y = i // BOARD_SIZE, j // BOARD_SIZE
                board_x, board_y = i % BOARD_SIZE, j % BOARD_SIZE

                cell_idx = cell_x * BOARD_SIZE + cell_y
                row.append(str(int(self.__cells[cell_idx].board[board_x, board_y])))
            board.append(' '.join(row))

        return '\n'.join(board)

def run_test(board):
    while board.done == NOT_DONE_YET:
        move = board.get_available_moves[0]
        board.move(*move)

def export_map(board):
    with open(MAP_EXPORT_FILE, 'w') as file:
        file.write(str(board))

def export_state(board):
    with open(STATE_EXPORT_FILE, 'w') as file:
        file.write(' '.join([str(b) for b in board.available_boards]))

def run_subprocess(file_name):
    kill = lambda process: process.kill()
    process = subprocess.Popen(
        [file_name]
    )

    timer = Timer(TIME_OUT, kill, [process])

    try:
        timer.start()
        process.wait()
    finally:
        timer.cancel()

def read_move():
    with open(MOVE_EXPORT_FILE) as file:
        board_idx, cell_idx = file.read().strip().split(' ')

    return int(board_idx), int(cell_idx)

def run_agent(turn):
    if turn == X:
        file_name = 'x.exe'
    if turn == O:
        file_name = 'o.exe'

    logger.debug('Executing the subprocess')
    run_subprocess(file_name)

    logger.debug('Reading the chosen move')
    move = read_move()

    return move

def run_game(board):
    logger.debug('running the game')

    turn = X
    while board.done == NOT_DONE_YET:
        board.print_board()
        logger.debug(f'Player {"Xs" if turn == X else "Os"} turn')

        logger.debug('Exporting the map')
        export_map(board)

        logger.debug('Ecporting the state')
        export_state(board)

        logger.debug('Running the agents')
        try:
            boards_idx, cell_idx = run_agent(turn)

            logger.info(f'Choosed move: ({boards_idx},{cell_idx})')
            board.move(boards_idx, cell_idx)

            logger.debug('Removing move.txt')
            os.remove(MOVE_EXPORT_FILE)
        except:
            board.announce_opponents_win()
            logger.error(f'There was an error while running the agent: {turn.text}')

        turn = O if turn == X else X

def parse_args():
    parser = argparse.ArgumentParser(prog='Super Tic-Tac-Toe Server')

    parser.add_argument('-t', '--test', help='Use this flag to test the server installation steps', action  = 'store_true', required=False)
    parser.add_argument('-r', '--run', help='use this flag to run players and see the result', action = 'store_true', required=False)
    parser.add_argument('-l', '--log', help='use this flag to log the game in a log file', action='store_true', required=False)
    parser.add_argument('-v', '--verbose', help='use this flag to log the game board after each move', action='store_true', required=False)
    parser.add_argument('-d', '--dir', help='specifies the loggers output directory', action='store', nargs=1)

    args = parser.parse_args(sys.argv[1:])
    return args

def main():
    global logger
    args = parse_args()
    
    board = Board()
    canvas.pack()
    
    level = logging.DEBUG if args.verbose else logging.INFO
    log_root = args.dir[0] if args.dir else '.\\'
    if args.log:
        log_file = f'{log_root}\\{str(int(time.time()*1000))}.log'
        logging.basicConfig(level=level, filename=log_file)
    else:
        logging.basicConfig(level=level)

    logger = logging.getLogger('Server')

    if args.test:
        logger.debug('Test mode is activated')
        run_test(board)
    elif args.run:
        logger.debug('Contest mode is activated')
        
        run_game(board)
    
    mainloop()

if __name__ == '__main__':
    main()

