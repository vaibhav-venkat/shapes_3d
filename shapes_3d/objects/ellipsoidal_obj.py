from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import save_dump

a = 40
b = 30
c = 80

density = 0.02
ellipsoid = Ellipsoid(
    density, x_outer_radius=a, y_outer_radius=b, z_outer_radius=c
).make_obj()

save_dump([ellipsoid], "out/ellipsoid.dump", 2 * max(a, b, c))
