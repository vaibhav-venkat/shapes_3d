from ..modules.patch_onion import PatchOnion
from ..modules.utils import save_dump
import numpy as np

sphere = PatchOnion(
    radii=np.array([50]),
    center=np.array([0, 0, 0]),
    density=np.array([1]),
    patch_area=5000,
    num_patches=8,
    patch_density=0.1,
)
base = sphere.onion_base()
patches = sphere.patches()
save_dump([base, patches], "out/patchy_sphere.dump", 50)
