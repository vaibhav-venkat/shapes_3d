from ..modules.onion import Onion
from ..modules.utils import save_dump
import numpy as np

R: np.ndarray = np.array([30, 20, 10, 5])
d: np.ndarray = np.array([0.5, 1, 0.2, 0.4])

onion = Onion(R, np.array([0, 0, 0]), d)

save_dump([onion], "onion.dump", np.sum(R))
