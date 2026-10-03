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
                print(i, len(self.allSolutions))
            i += 1

        self.allSolutions = np.array(self.allSolutions)

