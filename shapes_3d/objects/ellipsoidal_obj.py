from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import save_dump

a = 40
c = 70
d = 0.02
ellipsoid = Ellipsoid(d, -a, 0, c).make_obj()

save_dump([ellipsoid], "out/ellipsoid.dump", 2 * max(a, c))
