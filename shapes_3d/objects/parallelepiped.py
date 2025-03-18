import numpy as np

from shapes_3d.modules.parallelepiped import Parallelepiped
from shapes_3d.modules.utils import save_dump

thickness = np.array([[50, 20, 30], [20, 30, 30]])
density = np.array([1, 0.3])
points: np.ndarray = Parallelepiped(thickness, density, np.pi / 3, np.pi / 6).make_obj()
save_dump([points], "out/parall.dump", 100)  # I ain't spelling allat
