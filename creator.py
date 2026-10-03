from copy import deepcopy

import numpy as np
import solver as slv

class Creator(slv.Solver):
    def __init__(self):
        super().__init__()
        self.allSolutions = []

    def randomStart(self, filledOut):
        sudoku = slv.Sudoku()
        sudoku.randomInit(filledOut)
        self.load(sudoku)

    def create(self, amount, filledOut):
        i = 0
        while len(self.allSolutions) < amount:
            self.randomStart(filledOut)
            solution = self.solve()
            if solution:
                self.allSolutions += solution
                #print(i, len(self.allSolutions))
            i += 1

        self.allSolutions = np.array(self.allSolutions)

class TaskCreator(slv.Solver):
    def __init__(self):
        super().__init__()
        self.origin = None
        self.currentState = None
        self.tasks = []

    def loadOrigin(self, origin):
        self.origin = origin
        self.load(deepcopy(origin))

    def run(self, amount):
        while len(self.tasks) < amount:
            currentState = deepcopy(self.origin)
            previousState = deepcopy(self.origin)
            self.load(deepcopy(self.origin))
            while len(self.solutions) <= 1:
                self.load(currentState)
                previousState = deepcopy(self.sudoku)
                x, y = np.random.randint(low=0, high=9, size=2)
                self.cells[y][x].unsolve()
                self.sudoku.sudoku[y][x] = 0
                currentState = deepcopy(self.sudoku)
                self.update()
                self.solve()

            self.tasks.append(deepcopy(previousState.sudoku))


