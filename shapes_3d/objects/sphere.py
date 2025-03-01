from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import save_dump

R = 50
d = 0.05
sphere = Ellipsoid(d, R).make_obj()

save_dump([sphere], "out/sphere.dump", 2 * R)
