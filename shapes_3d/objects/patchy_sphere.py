from ..modules.patch_onion import PatchOnion
from ..modules.utils import save_dump
import numpy as np

sphere = PatchOnion(
    radii=np.array([50]),
    center=np.array([0, 0, 0]),
    density=np.array([1]),
    Y=500,
    X=20,
    patch_den=0.3,
)

base = sphere.onion_base()
patches = sphere.patches()
save_dump([base, patches], "out/sphere.dump", 50)
