from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import save_dump

R = 50
d = 0.5
sphere = Ellipsoid(d, R)

save_dump([sphere], "sphere.dump", R)
