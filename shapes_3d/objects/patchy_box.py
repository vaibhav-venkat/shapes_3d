from ..modules.patch_onion import PatchOnion
from ..modules.utils import save_dump, make_centers
import numpy as np

THICKNESS_MEAN: np.ndarray = np.array([10.0, 7.0, 6.0, 5.0, 4.0])
STD_THICKNESS: np.ndarray = np.array([1.5, 1.2, 0.5, 0.8, 1.0])
DENSITY = np.array([0.0, 0.05, 0.1, 0.03, 0.2])
L: float = 800
VOLUME_FRACTION: float = 0.05
PATCH_DENSITY: float = 0.3
Y: np.ndarray = np.array([300.0, 200.0, 900.0, 1500.0, 200.0, 3000.0])
X: int = 6

assert DENSITY.shape == STD_THICKNESS.shape == THICKNESS_MEAN.shape

radii_list: list = []
tgt: float = (L**3) * VOLUME_FRACTION
curr_vol: float = 0
sigma_ts: np.ndarray = np.sqrt(np.log(1 + (STD_THICKNESS / THICKNESS_MEAN) ** 2))
mu_ts: np.ndarray = np.log(THICKNESS_MEAN) - sigma_ts**2 / 2
while curr_vol < tgt:
    rad_tot: float = 0
    curr_sphere = np.random.lognormal(mu_ts, sigma_ts)
    curr_vol += float(np.sum(curr_sphere) ** 3) * np.pi * 4 / 3
    if curr_vol > tgt:
        break
    radii_list.append(curr_sphere)
radii: np.ndarray = np.array(radii_list)
N: int = radii.shape[0]


max_r: float = np.max(radii.sum(axis=1))
print("making the centers")
centers = make_centers(N, -L / 2 + max_r, L / 2 - max_r, 2 * max_r)
onion_list = []
patch_list = []
print("making the patches and shells")
for i in range(N):
    if (i + 1) % 100 == 0 or i == 0 or i == N - 1:
        print("N =", i + 1, "out of", N)
    shell = PatchOnion(radii[i], centers[i], DENSITY, Y, X, PATCH_DENSITY)
    onion_list.extend(shell.onion_base())
    patches = shell.patches() + centers[i]
    patch_list.extend(patches)

onion_pts: np.ndarray = np.array(onion_list)
patch_pts: np.ndarray = np.array(patch_list)

save_dump([onion_pts, patch_pts], "out/patchy_box.dump", box_len=L)
