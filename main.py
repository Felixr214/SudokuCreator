import numpy as np
import creator as crt
import solver as slv

np.random.seed(1)

c = crt.Creator()
c.create(1, 30)
#print(c.allSolutions.shape)

tc = crt.TaskCreator()
origin = slv.Sudoku()
origin.sudoku = c.allSolutions[0]
tc.loadOrigin(origin)
tc.run(5)