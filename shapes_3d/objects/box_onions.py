import numpy as np
from ..modules.onion import Onion
from pathlib import Path
from ..modules.utils import save_dump, make_centers

ts = np.array([10.0, 7.0, 6.0, 5.0, 4.0])
std_ts = np.array([1.5, 1.2, 0.5, 0.8, 1.0])
density = np.array([0.0, 0.05, 0.1, 0.03, 0.2])
L: float = 800
VOL_FR: float = 0.05
# ts = np.array([20, 10])
# std_ts = np.array([3, 4])
# L = 1000
# VOL_FR = 0.1
# density = np.array([0.1, 0.05])
assert density.shape == std_ts.shape == ts.shape

radii = []
tgt = (L**3) * VOL_FR
curr_vol: float = 0
sigma_ts: np.ndarray = np.sqrt(np.log(1 + (std_ts / ts) ** 2))
mu_ts: np.ndarray = np.log(ts) - sigma_ts**2 / 2
while curr_vol < tgt:
    rad_tot: float = 0
    curr_sphere = np.random.lognormal(mu_ts, sigma_ts)
    curr_vol += float(np.sum(curr_sphere) ** 3) * np.pi * 4 / 3
    if curr_vol > tgt:
        break
    radii.append(curr_sphere)
radii = np.array(radii)
N: int = radii.shape[0]


max_r: float = np.max(radii.sum(axis=1))
centers = make_centers(N, -L / 2 + max_r, L / 2 - max_r, 2 * max_r)
pts = []
for i in range(N):
    if (i + 1) % 100 == 0 or i == 0 or i == N - 1:
        print("N =", i + 1, "out of", N)
    shell = Onion(radii[i], centers[i], density)
    pts.extend(shell.pts)
pts = np.array(pts)


def save_coords(points: np.ndarray, filename: str = "out.txt") -> None:
    """
    Save coordinates to a file
    """
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(filename, points, fmt="%.6f", header="X Y Z shell", comments="")
    print("saved to", filename)


save_coords(pts, "out/box_onion.txt")
save_dump([pts], "out/box_onion.dump", L)
