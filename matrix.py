import numpy as np
from scipy.io import savemat

# Map with camera locations represented as a matrix
m = np.array([[0,0,0,0,0,0,2,0,0],
              [0,0,4,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0,0],
              [0,0,3,0,0,0,1,0,0],
              [0,0,0,0,0,0,0,0,0],
              [0,0,0,0,0,0,0,0,0]])
dm = {'map': m}
savemat("map.mat", dm)

