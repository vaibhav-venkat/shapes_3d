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


def gen_points_faiss(
    n_pts: int, min_val: float, max_val: float, dist: float, n_batch: int = 100
) -> np.ndarray:
    """
    Generate points with minimum distance using Faiss and batching.

    Params:
    n_pts -- number of points
    min_val -- the minmum value on the interval
    max_al -- the maximum value on the interval
    dist -- the minimum distance between each R^3 point
    n_batch -- the number of points to generate per batch
    """
    dim = 3
    nlist = 400  # Clusters
    quantizer = faiss.IndexFlatL2(dim)
    index = faiss.IndexIVFFlat(quantizer, dim, nlist)
    training_data = np.random.uniform(
        min_val, max_val, size=(int(2000 * np.sqrt(N)), 3)
    ).astype("float32")
    index.train(training_data)

    # index = faiss.IndexHNSWFlat(dim, 20)

    pts = []
    i = 0

    while i < n_pts:
        remaining = n_pts - i
        current_batch_size = min(n_batch, remaining)

        # Generate a batch of candidate points
        batch = np.random.uniform(
            min_val, max_val, size=(current_batch_size, dim)
        ).astype("float32")

        if i > 0:
            # Neighboring points
            D, _ = index.search(batch, 1)
            valid = np.sqrt(D[:, 0]) >= dist  # Check distances
            valid_points = batch[valid]
        else:
            valid_points = batch

        index.add(valid_points)
        pts.extend(valid_points)
        i += valid_points.shape[0]
        if valid_points.shape[0]:
            print(i, "out of", N)

    return np.array(pts[:n_pts])


max_r: float = np.max(radii.sum(axis=1))
centers = gen_points_faiss(N, -L / 2 + max_r, L / 2 - max_r, 2 * max_r)
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
        for i in range(0, len(points)):
            if points[i].shape[1] == 4:
                for j in range(points[i].shape[0]):
                    f.write(
                        f"{j + 1} {int(points[i][j][3] + i)} {points[i][j][0]:.6f} {points[i][j][1]:.6f} {points[i][j][2]:.6f}\n"
                    )
            else:
                for j, (x, y, z) in enumerate(points[i], start=1):
                    f.write(f"{j} {i + 1} {x:.6f} {y:.6f} {z:.6f}\n")
        print("dumped to", filename)


save_dump([onion_pts, patch_pts], box_len=L)
