from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import save_dump

x_length = 40
z_length = 70
density = 0.02
ellipsoid = Ellipsoid(density, -x_length, 0, z_length).make_obj()

save_dump([ellipsoid], "out/ellipsoid.dump", 2 * max(x_length, z_length))
