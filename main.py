import numpy as np
from copy import deepcopy

def pos2square(x, y):
    x = x // 3
    y = y // 3
    return x, y

def getRow(arr, i):
    if 0 > i > 8:
        return []
    return arr[i]

def getCol(arr, j):
    if 0 > j > 8:
        return []
    return arr[:,j]

def getSquare(arr, i, j):
    x0 = j * 3
    x1 = x0 + 3
    y0 = i * 3
    if i < 0 or i > 8 or j < 0 or j > 8:
        return []

    square = np.array([
        arr[y0,x0:x1],
        arr[y0+1, x0:x1],
        arr[y0+2, x0:x1],
    ]).reshape([9])

    return square

def testArr(arr):
    d = {}
    for a in arr:
        d[a] = 0
    for a in arr:
        if a != 0:
            if d[a] > 0:
                return False
            d[a] += 1
    return True

def getSquareById(arr, id):
    if id == 0:
        i, j = 0, 0
    elif id == 1:
        i, j = 0, 1
    elif id == 2:
        i, j = 0, 2
    elif id == 3:
        i, j = 1, 0
    elif id == 4:
        i, j = 1, 1
    elif id == 5:
        i, j = 1, 2
    elif id == 6:
        i, j = 2, 0
    elif id == 7:
        i, j = 2, 1
    elif id == 8:
        i, j = 2, 2
    else:
        return []

    return getSquare(arr, i, j)

def string2Sudoku(sudoku_str):
    sudoku = Sudoku()

    for x in range(9):
        for y in range(9):
            str_index = y*9+x
            value = int(sudoku_str[str_index])
            sudoku.sudoku[y][x] = value

    return sudoku

def handleRedundancy(arr):
    values = []
    progress = 0
    for cell in arr:
        if cell.isFinished:
            values.append(cell.value)
    for cell in arr:
        if not cell.isFinished:
            for value in values:
                progress += cell.remove(value)
            if len(cell.possibleValues) == 0:
                # print(cell.x,cell.y)
                return 0, True
    return progress, False

def handleLastRemaining(arr):
    dist = np.zeros(9)
    value = 0
    progress = 0
    for i in range(9):
        cell = arr[i]
        if not cell.isFinished:
            for value in cell.possibleValues:
                dist[value - 1] += 1
        else:
            value = cell.value
            dist[value - 1] += 2

    if 1 in dist:
        for a in range(9):
            if dist[a] == 1:
                value = a + 1
        for cell in arr:
            if value in cell.possibleValues and not cell.isFinished:
                cell.solveWithValue(value)
                progress += 1
                return 1
    return progress

class Sudoku:
    def __init__(self):
        self.sudoku = np.zeros([9, 9], dtype=int)

    def isFinished(self):
        if 0 in self.sudoku:
            return False
        if not self.check():
            return False
        return True

    def check(self):
        for i in range(9):
            if not testArr(getRow(self.sudoku, i)):
                return False
            if not testArr(getCol(self.sudoku, i)):
                return False
            if not testArr(getSquareById(self.sudoku, i)):
                return False
        return True

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.possibleValues = np.arange(1, 10, dtype=int).tolist()
        self.isFinished = False
        self.value = 0

    def solve(self):
        if self.isFinished:
            return False
        if len(self.possibleValues) == 1:
            self.isFinished = True
            self.value = self.possibleValues[0]
        return False

    def remove(self, value):
        value = value
        if value in self.possibleValues:
            self.possibleValues.remove(value)
            #self.solve()
            return 1
        return 0

    def solveWithValue(self, value):
        if value in self.possibleValues:
            self.value = value
            self.isFinished = True
            self.possibleValues = [value]
            return True
        return False

class Solver:
    def __init__(self, depth=0):
        self.cells = None
        self.sudoku = None
        self.maxDepth = 100
        self.depth = depth
        self.solutions = []

    def load(self, sudoku):
        self.sudoku = sudoku
        self.cells = np.array([[Cell(x, y) for x in range(9)] for y in range(9)])
        for y in range(9):
            for x in range(9):
                value = sudoku.sudoku[y][x]
                if value != 0:
                    self.cells[y][x].solveWithValue(value)

    def removeRedundant(self, i):
        progress = 0
        row = getRow(self.cells, i)
        col = getCol(self.cells, i)
        square = getSquareById(self.cells, i)

        progress_, fail = handleRedundancy(row)
        if fail:
            return 0, True
        progress += progress_

        progress_, fail = handleRedundancy(col)
        if fail:
            return 0, True
        progress += progress_

        progress_, fail = handleRedundancy(square)
        if fail:
            return 0, True
        progress += progress_

        return progress, False

    def removeAllRedundant(self):
        progress = 0
        for a in range(9):
            p, fail = self.removeRedundant(a)
            if fail:
                return 0, fail
            progress += p
        return progress, False

    def solveLastRemaining(self, i):
        row = getRow(self.cells, i)
        col = getCol(self.cells, i)
        square = getSquareById(self.cells, i)

        progress = handleLastRemaining(row)
        if progress > 0:
            return 1

        progress = handleLastRemaining(col)
        if progress > 0:
            return 1

        progress = handleLastRemaining(square)
        if progress > 0:
            return 1

        return progress

    def solveAllLastRemaining(self):
        progress = 0
        for a in range(9):
            progress += self.solveLastRemaining(a)
            if progress > 0:
                return 1
        return progress

    def recursiveStep(self):
        if self.depth == self.maxDepth:
            print("reached max recursion depth")
            quit()

        cells_ = self.cells.flatten().tolist()
        cells_.sort(key=lambda x: len(x.possibleValues), reverse=False)
        x, y = 0, 0
        for a in range(81):
            if len(cells_[a].possibleValues) >= 2 and not cells_[a].isFinished:
                x, y = cells_[a].x, cells_[a].y
                break

        for value in self.cells[y][x].possibleValues:
            solver_ = Solver(self.depth + 1)
            solver_.load(deepcopy(self.sudoku))
            solver_.cells[y][x].solveWithValue(value)
            solver_.update()
            solution = solver_.solve()
            if solution:
                self.solutions += solution
        return self.solutions

    def update(self):
        sudoku = np.zeros([9, 9], dtype=int)
        for x in range(9):
            for y in range(9):
                cell = self.cells[y][x]
                cell.solve()
                if cell.isFinished:
                    sudoku[y][x] = cell.value
                    self.sudoku.sudoku = sudoku
        return self.sudoku.check()

    def solve(self):
        while not self.sudoku.isFinished():
            progress, fail = self.removeAllRedundant()
            if fail:
                return None
            if progress > 0:
                if not self.update():
                    return None
            progress += self.solveAllLastRemaining()
            if progress > 0:
                if not self.update():
                    return None
            elif not self.sudoku.isFinished():
                return self.recursiveStep()

        self.solutions.append(self.sudoku.sudoku)
        return self.solutions

start_field1 = "000300002000592084050006000306910007070008900508240600900000000200800306000460010"
start_field2 = "408030005070000002010007000004000300890700060600095000980304500302800910100200080"
start_field2_1 = "408000005070000002010007000004000300890700060600095000980304500302800910100200080"
start_field3 = "093070060080000000000600001800000030034009005100040000000005200067090010400000000"
start_field4 = "005008069060240001000001073000000000150382000084906050001020906070804030000000700"

start_fields = [start_field1, start_field2, start_field3, start_field4, start_field2_1]
i = 1
for start_field in start_fields:
    print(f"id: {i}")
    i += 1
    sudoku = string2Sudoku(start_field)
    s = Solver()
    s.load(sudoku)
    solutions = s.solve()
    print(f"found {len(solutions)} solutions")
    for solution in solutions:
        print(solution)
    print()
