from ..modules.patch_onion import PatchOnion
from ..modules.utils import save_dump
import numpy as np

onion = PatchOnion(
    radii=np.array([50, 30, 10]),
    center=np.array([0, 0, 0]),
    density=np.array([1, 0.5, 0.25]),
    Y=700,
    X=20,
    patch_den=0.4,
)

base = onion.onion_base()
patches = onion.patches()
save_dump([base, patches], "out/sphere.dump", 50 + 30 + 10)
