from ..modules.patch_onion import PatchOnion
from ..modules.utils import save_dump
import numpy as np

onion = PatchOnion(
    radii=np.array([50, 30, 10]),
    center=np.array([0, 0, 0]),
    density=np.array([1, 0.5, 0.25]),
    patch_area=np.array([20000, 10000, 12000, 8000, 9000, 17000, 8000, 9000]),
    num_patches=8,
    patch_density=0.4,
)

# patch_area=np.array([1000, 5000, 6000, 8000, 4000, 7000, 5000, 3000]),
# patch_area=np.array([10000, 8000, 12000, 13000, 8000, 17000, 6000, 9000]),
# patch_area=np.array([20000, 10000, 12000, 8000, 9000, 17000, 8000, 9000]),
base = onion.onion_base()
patches = onion.patches()
save_dump([base, patches], "out/patch_onion.dump", 50 + 30 + 10)
