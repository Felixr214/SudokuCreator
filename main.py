import numpy as np
import creator as crt
import solver as slv

np.random.seed(1)

ds = crt.Dataset("dataset2", 10, 10, 10, 3, True)
ds.build()

data = ds.read("train")[0]
print(len(data))
