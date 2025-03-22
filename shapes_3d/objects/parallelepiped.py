import numpy as np

from shapes_3d.modules.parallelepiped import Parallelepiped
from shapes_3d.modules.utils import save_dump

# thickness = np.array([[50, 20, 30], [20, 30, 30]])
thickness = np.array([[50, 20, 30], [10, 20, 10]])
density = np.array([0.5, 0.06])
obj: Parallelepiped = Parallelepiped(thickness, density, np.pi / 3, np.pi / 3)
points: np.ndarray = obj.make_obj()
save_dump([points], "out/parall.dump", obj.get_final_bounds() + 3)
