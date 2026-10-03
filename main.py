import numpy as np
import creator as crt

np.random.seed(1)

ds = crt.Dataset("dataset2", 100000, 1000, 1000, 4, True)
ds.build()

data = ds.read("train")[0]
print(len(data))
