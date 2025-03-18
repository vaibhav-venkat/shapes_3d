import numpy as np

from shapes_3d.modules.parallelepiped import Parallelepiped
from shapes_3d.modules.utils import save_dump

thickness = np.array([[50, 20, 30], [20, 30, 20]])
density = np.array([0.1, 0.5])
points: np.ndarray = Parallelepiped(thickness, density, np.pi / 3, np.pi / 3).make_obj()
save_dump([points], "out/parall.dump", 100)
