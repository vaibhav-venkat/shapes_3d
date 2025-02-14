from patch_onion import PatchOnion
import numpy as np
import faiss
from pathlib import Path

ts: np.ndarray = np.array([10.0, 7.0, 6.0, 5.0, 4.0])
std_ts: np.ndarray = np.array([1.5, 1.2, 0.5, 0.8, 1.0])
density = np.array([0.0, 0.05, 0.1, 0.03, 0.2])
L: float = 800
VOL_FR: float = 0.15
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
    # divide the box into equal size
    num_cells: int = int(np.floor((max_pt - min_pt) / min_L))
    cell_size: float = (max_pt - min_pt) / num_cells
    grid = [
        [[[] for _ in range(num_cells)] for _ in range(num_cells)]
        for _ in range(num_cells)
    ]  # (x, y, z)
    pts: np.ndarray = np.zeros((N, 3))
    num_pts: int = 0
    while num_pts < N:
        # random point
        R: np.ndarray = np.random.uniform(min_pt, max_pt, 3)
        x_c: int = int((R[0] - min_pt) // cell_size)
        y_c: int = int((R[1] - min_pt) // cell_size)
        z_c: int = int((R[2] - min_pt) // cell_size)
        good = True
        min_x_rng = 0 if x_c == 0 else -1
        max_x_rng = 0 if x_c == (num_cells - 1) else 1
        for i in range(min_x_rng, max_x_rng):
            min_y_rng = 0 if y_c == 0 else -1
            max_y_rng = 0 if y_c == (num_cells - 1) else 1
            for j in range(min_y_rng, max_y_rng):
                min_z_rng = 0 if z_c == 0 else -1
                max_z_rng = 0 if z_c == (num_cells - 1) else 1
                for k in range(min_z_rng, max_z_rng):
                    for a in range(len(grid[x_c + i][y_c + j][z_c + k])):
                        r1: np.ndarray = grid[x_c + i][y_c + j][z_c + k][a]
                        dist = np.linalg.norm(r1 - R)
                        if dist <= min_L:
                            good = False
                            break
        if good:
            grid[x_c][y_c][z_c].append(R)
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
    shell = PatchOnion(radii[i], centers[i], density, Y, X)
    onion_list.extend(shell.onion_base())
    patch_list.extend(shell.patches() + centers[i])

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
