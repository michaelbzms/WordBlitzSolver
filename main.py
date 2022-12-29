import time
from copy import copy

import pyautogui
import unicodedata as ud
import pygtrie


def read_dict(file: str):
    with open(file, 'r') as f:
        words = f.read().split('\n')
    # preprocess
    d = {ord('\N{COMBINING ACUTE ACCENT}'): None}
    for i in range(len(words)):
        words[i] = words[i].strip().lower()
        words[i] = ud.normalize('NFD', words[i]).translate(d)
    return words


def read_grid(file: str):
    with open(file, 'r', encoding='utf-8') as f:
        grid = f.read().split('\n')
        grid = [row.split(' ') for row in grid]
    return grid


def _rec_solve(trie, grid, prefix: str, i, j, path):
    solutions = []
    # do not repeat path
    if (i, j) in path:
        return []
    # keep track of path
    path.append((i, j))
    # check if current prefix is a word
    if len(prefix) > 1 and trie.has_key(prefix):
        # print(len(prefix), prefix, path)
        solutions.append((len(prefix), prefix, copy(path)))
    # check neighbours up
    if i > 0:
        if trie.has_subtrie(prefix + grid[i-1][j]): solutions += _rec_solve(trie, grid, prefix + grid[i-1][j], i-1, j, copy(path))
        if j > 0 and trie.has_subtrie(prefix + grid[i-1][j-1]): solutions += _rec_solve(trie, grid, prefix + grid[i-1][j-1], i-1, j-1, copy(path))
        if j < 3 and trie.has_subtrie(prefix + grid[i-1][j+1]): solutions += _rec_solve(trie, grid, prefix + grid[i-1][j+1], i-1, j+1, copy(path))
    # check neighbours down
    if i < 3:
        if trie.has_subtrie(prefix + grid[i+1][j]): solutions += _rec_solve(trie, grid, prefix + grid[i+1][j], i+1, j, copy(path))
        if j > 0 and trie.has_subtrie(prefix + grid[i+1][j-1]): solutions += _rec_solve(trie, grid, prefix + grid[i+1][j-1], i+1, j-1, copy(path))
        if j < 3 and trie.has_subtrie(prefix + grid[i+1][j+1]): solutions += _rec_solve(trie, grid, prefix + grid[i+1][j+1], i+1, j+1, copy(path))
    # check horizontal neighbours
    if j > 0 and trie.has_subtrie(prefix + grid[i][j-1]): solutions += _rec_solve(trie, grid, prefix + grid[i][j-1], i, j-1, copy(path))
    if j < 3 and trie.has_subtrie(prefix + grid[i][j+1]): solutions += _rec_solve(trie, grid, prefix + grid[i][j+1], i, j+1, copy(path))
    return solutions


def solve(trie, grid):
    solutions = []
    for i in range(4):
        for j in range(4):
            solutions += _rec_solve(trie, grid, str(grid[i][j]), i, j, [])
    return solutions


def draw_solutions(solutions, limit):
    for n, (length, word, path) in enumerate(solutions):
        if n >= limit:
            break
        print(f'{n+1}. {word} ({length} letters)')
        grid = [[' ', ' ', ' ', ' '] for _ in range(4)]  # 4x4 grid
        for k, (x, y) in enumerate(path):
            grid[x][y] = f'{k+1}'
        for i in range(4):
            for j in range(4):
                print(f'|{grid[i][j]}', end='')
            print('|')
        print('')


def create_positions() -> dict:
    start_x = 132
    start_y = 527
    distance = 106
    positions = {}
    for i in range(4):
        for j in range(4):
            positions[(i, j)] = (start_x + j * distance, start_y + i * distance)
    print(positions)
    return positions


def play_solutions(solutions, limit: int):
    # Position of buttons
    positions = create_positions()
    # play the solutions
    for length, word, path in solutions[:limit]:
        print(positions[path[0]])
        pyautogui.moveTo(positions[path[0]], duration=0.0001)
        pyautogui.mouseDown()
        for p in path[1:]:
            pyautogui.moveTo(positions[p], duration=0.0001)
        pyautogui.mouseUp()
        time.sleep(0.01)


if __name__ == '__main__':
    # how many word to limit ourselves to
    limit = 100

    # read dict of words
    words = read_dict('Greek.dic')

    # index wordz as trie
    trie = pygtrie.CharTrie()
    for w in words:
        trie[w] = w

    # read 4x4 grid
    grid = read_grid('grid.txt')

    # solve
    print('Solving...')
    solutions = solve(trie, grid)
    print('Done')

    # sort by len
    sorted_solutions = sorted(solutions, key=lambda x: -x[0])

    # remove duplicates
    final_solutions = [sorted_solutions[0]]
    seen = set(sorted_solutions[0][1])
    for i in range(1, len(sorted_solutions)):
        if sorted_solutions[i][1] not in seen:
            final_solutions.append(sorted_solutions[i])
        seen.add(sorted_solutions[i][1])

    # draw solutions
    play_solutions(final_solutions, limit=limit)
