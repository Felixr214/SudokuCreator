import numpy as np
import creator as crt

np.random.seed(1)

ds = crt.Dataset("dataset", 1000000, 10000, 10000, 10, 50, True)
ds.build()

data = ds.read("train")[0]
print(len(data))
