from ..modules.onion import Onion
from ..modules.utils import save_dump
import numpy as np

thickness: np.ndarray = np.array([10.0, 7.0, 6.0, 5.0, 4.0])
density: np.ndarray = np.array([0, 0.05, 0.1, 0.03, 0.2])
onion_pts = Onion(thickness, np.array([0, 0, 0]), density).construct_pts()

save_dump([onion_pts], "out/onion.dump", 2 * np.sum(thickness))
