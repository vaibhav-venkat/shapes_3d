from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import save_dump

a = 20
c = 40
d = 0.5
ell = Ellipsoid(d, a, 0, c)

save_dump([ell], "sphere.dump", max(a, c))
