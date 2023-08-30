#define BOARD_SIZE 3

#define X_VALUE 1
#define O_VALUE -1
#define EMPTY_CELL 0

#define MAP_EXPORT_FILE "map.txt"
#define STATE_EXPORT_FILE "state.txt"
#define MOVE_EXPORT_FILE "move.txt"

#include <iostream>
#include <fstream>

using namespace std;

struct Cell
{
    int board[BOARD_SIZE][BOARD_SIZE];
};

Cell cells[BOARD_SIZE * BOARD_SIZE];
bool boards[BOARD_SIZE * BOARD_SIZE];

void read_whole_map()
{
    ifstream file(MAP_EXPORT_FILE);

    int lim = BOARD_SIZE * BOARD_SIZE;
    for (int i = 0; i < lim; i++)
    {
        for (int j = 0; j < lim; j++)
        {
            int cell_x = i / BOARD_SIZE;
            int cell_y = j / BOARD_SIZE;
            int board_x = i % BOARD_SIZE;
            int board_y = j % BOARD_SIZE;
            int cell_idx = cell_x * BOARD_SIZE + cell_y;

            int element;
            file >> cells[cell_idx].board[board_x][board_y];
        }
    }

    file.close();
}

void read_available_boards()
{
    ifstream file(STATE_EXPORT_FILE);

    while (!file.eof())
    {
        int e;
        file >> e;
        boards[e] = true;
    }

    file.close();
}

void export_move(int board_idx, int cell_idx)
{
    cout << board_idx << " " << cell_idx << endl;
    ofstream file(MOVE_EXPORT_FILE);

    file << board_idx << " " << cell_idx;
    file.close();
}

void move()
{
    // Start your code here
    int chosen_board_idx = 0;
    int chosen_cell_idx = 0;

    // Sample code
    int lim = BOARD_SIZE * BOARD_SIZE;
    bool done = false;
    for (int t = 0; t < lim; t++)
    {
        if (done)
            break;
        if (boards[t] == 1)
        {
            for (int i = 0; i < BOARD_SIZE; i++)
            {
                if (done)
                    break;
                for (int j = 0; j < BOARD_SIZE; j++)
                {
                    if (cells[t].board[i][j] == 0)
                    {
                        int cell_idx = i * BOARD_SIZE + j;

                        chosen_board_idx = t;
                        chosen_cell_idx = cell_idx;
                        done = true;
                        break;
                    }
                }
            }
        }
    }

    // End yout code here

    export_move(chosen_board_idx, chosen_cell_idx);
}

int main()
{
    read_whole_map();
    read_available_boards();
    move();

    return 0;
}