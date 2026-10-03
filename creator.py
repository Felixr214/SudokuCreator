from copy import deepcopy
import numpy as np
import h5py

import solver as slv

class Creator(slv.Solver):
    def __init__(self):
        super().__init__()
        self.allSolutions = []

    def randomStart(self, filledOut):
        sudoku = slv.Sudoku()
        sudoku.randomInit(filledOut)
        self.load(sudoku)

    def create(self, amount, filledOut, solutionsPerStart):
        i = 0
        while len(self.allSolutions) < amount:
            self.randomStart(filledOut)
            solution = self.solve()
            if solution:
                self.allSolutions += solution[:solutionsPerStart]
                #print(i, len(self.allSolutions))
            i += 1

        self.allSolutions = np.array(self.allSolutions)

class TaskCreator(slv.Solver):
    def __init__(self):
        super().__init__()
        self.origin = None
        self.currentState = None
        self.tasks = []
        self.labels = []

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

class Dataset:
    def __init__(self, name, trainSize, valSize, testSize, taskPerSolution, init=True):
        self.filename = f"datasets/{name}.h5"
        self.testSize = testSize
        self.trainSize = trainSize
        self.valSize = valSize
        self.tasksPerSolution = taskPerSolution

        if init:
            with h5py.File(self.filename, "w") as f:
                # Create groups for each split
                train_group = f.create_group("train")
                val_group   = f.create_group("val")
                test_group  = f.create_group("test")

                # Add features and labels inside each split group
                groups = [train_group, val_group, test_group]
                for group in groups:
                    group.create_dataset("features", shape=(0, 9, 9), maxshape=(None, 9, 9), dtype="float32", chunks=(1000, 9, 9))
                    group.create_dataset("labels", shape=(0, 9, 9), maxshape=(None, 9, 9), dtype="float32", chunks=(1000, 9, 9))

    def write(self, group, features, labels):
        # Ensure inputs are contiguous float32 numpy arrays with shape (N, 9, 9)
        features = np.asarray(features, dtype=np.float32)
        labels = np.asarray(labels, dtype=np.float32)

        if features.shape != labels.shape:
            raise ValueError(
                f"Shape mismatch: features {features.shape} vs labels {labels.shape}"
            )

        num_samples = features.shape[0]

        # Open in 'a' mode (read/write if exists, creates if not)
        with h5py.File(self.filename, "a") as f:
            x_ds = f[f"{group}/features"]
            y_ds = f[f"{group}/labels"]

            # 1. Resize datasets to fit the new batch
            curr_len = x_ds.shape[0]
            new_len = curr_len + num_samples

            x_ds.resize(new_len, axis=0)
            y_ds.resize(new_len, axis=0)

            # 2. Write data to the appended slice
            x_ds[curr_len:new_len] = features
            y_ds[curr_len:new_len] = labels

    def read(self, group):
        # Example: Reading validation features
        with h5py.File(self.filename, "r") as f:
            x = f[f"{group}/features"][:]
            y = f[f"{group}/labels"][:]
        return x, y

    def createSet(self, name, size):
        print(f"Build {name}_set")
        crt = Creator()
        tcrt = TaskCreator()
        sdk = slv.Sudoku()

        crt.create(size // self.tasksPerSolution, 30, max(1,int(size*0.1)))
        labels = crt.allSolutions[:size // self.tasksPerSolution]

        numFeatures = 0
        numLabels = 0

        for label in labels:
            sdk.sudoku = label
            tcrt.loadOrigin(sdk)
            tcrt.run(self.tasksPerSolution)
            features = deepcopy(tcrt.tasks)
            label_ = np.repeat([label], self.tasksPerSolution, axis=0)
            self.write(name, features, label_)
            numFeatures += len(features)
            numLabels += len(label_)
            print(numFeatures, numLabels)

    def build(self):
        self.createSet("train", self.trainSize)
        self.createSet("val", self.valSize)
        self.createSet("test", self.testSize)