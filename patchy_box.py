from patch_onion import PatchOnion
import numpy as np
from pathlib import Path
from spaced_grid import SpacedGrid

ts: np.ndarray = np.array([10.0, 7.0, 6.0, 5.0, 4.0])
std_ts: np.ndarray = np.array([1.5, 1.2, 0.5, 0.8, 1.0])
density = np.array([0.0, 0.05, 0.1, 0.03, 0.2])
L: float = 800
VOL_FR: float = 0.15
patch_den: float = 0.3
Y: np.ndarray = np.array([300.0, 200.0, 900.0, 1500.0, 200.0, 3000.0])
X: int = 6

assert density.shape == std_ts.shape == ts.shape

radii_list: list = []
tgt: float = (L**3) * VOL_FR
curr_vol: float = 0
sigma_ts: np.ndarray = np.sqrt(np.log(1 + (std_ts / ts) ** 2))
mu_ts: np.ndarray = np.log(ts) - sigma_ts**2 / 2
while curr_vol < tgt:
    rad_tot: float = 0
    curr_sphere = np.random.lognormal(mu_ts, sigma_ts)
    curr_vol += float(np.sum(curr_sphere) ** 3) * np.pi * 4 / 3
    if curr_vol > tgt:
        break
    radii_list.append(curr_sphere)
radii: np.ndarray = np.array(radii_list)
N: int = radii.shape[0]


def make_centers(N: int, min_pt: float, max_pt: float, min_L: float) -> np.ndarray:
    grid = SpacedGrid(min_pt, max_pt, min_L)
    grid.construct()
    pts: np.ndarray = np.zeros((N, 3))
    num_pts: int = 0
    while num_pts < N:
        # random point
        R: np.ndarray = np.random.uniform(min_pt, max_pt, 3)
        if not grid.overlap(R):
            i, j, k = grid.get_cell(R)
            grid.add(i, j, k, R)
            pts[num_pts] = R
            num_pts += 1
    return pts


max_r: float = np.max(radii.sum(axis=1))
centers = make_centers(N, max_r, L - max_r, 2 * max_r) - L / 2
onion_list = []
patch_list = []
for i in range(N):
    if (i + 1) % 100 == 0 or i == 0 or i == N - 1:
        print("N =", i + 1, "out of", N)
    shell = PatchOnion(radii[i], centers[i], density, Y, X, patch_den)
    onion_list.extend(shell.onion_base())
    patches = shell.patches() + centers[i]
    patch_list.extend(patches)

onion_pts: np.ndarray = np.array(onion_list)
patch_pts: np.ndarray = np.array(patch_list)


def save_dump(points, filename="out/patches.dump", box_len=1000):
    """
    Save coordinates to a dump file, for use with OVITO
    """
    num = sum(pt.shape[0] for pt in points)
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w") as f:
        f.write("ITEM: TIMESTEP\n0\n")
        f.write(f"ITEM: NUMBER OF ATOMS\n{num}\n")
        f.write(
            f"ITEM: BOX BOUNDS pp pp pp\n{-box_len // 2} {box_len // 2}\n{-box_len // 2} {box_len // 2}\n{-box_len//2} {box_len//2}\n"
        )
        f.write("ITEM: ATOMS id type x y z\n")
        max_type = 0
        for i in range(0, len(points)):
            if points[i].shape[1] == 4:
                for j in range(points[i].shape[0]):
                    f.write(
                        f"{j + 1} {int(points[i][j][3] + i)} {points[i][j][0]:.6f} {points[i][j][1]:.6f} {points[i][j][2]:.6f}\n"
                    )
                    max_type = max(max_type, int(points[i][j][3]))
            else:
                for j, (x, y, z) in enumerate(points[i], start=1):
                    f.write(f"{j} {i + 1 + max_type} {x:.6f} {y:.6f} {z:.6f}\n")
        print("dumped to", filename)


save_dump([onion_pts, patch_pts], box_len=L)
