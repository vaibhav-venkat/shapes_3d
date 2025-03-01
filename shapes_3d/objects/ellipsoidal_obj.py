from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import save_dump

a = 40
c = 70
d = 0.02
ell = Ellipsoid(d, a, 0, c).make_obj()

save_dump([ell], "out/ellipsoid.dump", 2 * max(a, c))
