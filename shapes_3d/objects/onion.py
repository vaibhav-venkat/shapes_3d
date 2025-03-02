from ..modules.onion import Onion
from ..modules.utils import save_dump
import numpy as np

R: np.ndarray = np.array([20, 5, 7])
d: np.ndarray = np.array([2, 0.03, 0.07])

onion = Onion(R, np.array([0, 0, 0]), d).construct_pts()

save_dump([onion], "out/onion.dump", 2 * np.sum(R))
