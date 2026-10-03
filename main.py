import numpy as np
import creator as crt

np.random.seed(1)

c = crt.Creator()
c.create(100, 30)

print(c.allSolutions.shape)
