from ..modules.onion import Onion
from ..modules.utils import save_dump
import numpy as np

R: np.ndarray = np.array([10.0, 7.0, 6.0, 5.0, 4.0])
d: np.ndarray = np.array([0, 0.05, 0.1, 0.03, 0.2])
pts = []
onion = Onion(R, np.array([0, 0, 0]), d).construct_pts()
for o in onion:
    if -2 <= o[0] <= 2:
        pts.append(o)

save_dump([np.array(pts)], "out/onion.dump", 2 * np.sum(R))
