import numpy as np
import faiss  # NOTE: This can run on Nvidia GPU's with faiss_gpu package
import time
from ellipsoid import Ellipsoid

# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

L = 1000  # Length
R_OM = 30.0  # Outer radius mean
R_OS = 5.0  # Outer radius standard deviation
R_IM = 20.0  # Inner radius mean
R_IS = 3.0  # Inner radius standard deviatoin
VOL_FR = 0.1  # Volume Fraction, dimensions L^(-3)
D1 = 0.1  # Density of core, in points per unit volume
D2 = 0.05  # Density of shell, in points per unit volume.


def save_coords(points, filename="out.txt"):
    """
    Save coordinates to a file
    """
    np.savetxt(filename, points, fmt="%.2f", delimiter=" ", header="X Y Z")


# TODO: make dist dynamic based on R_outer
# NOTE: Find info about faiss: https://github.com/facebookresearch/faiss
# PERF: Efficient but approximate, IndexFlatL2 is exact but takes a large amount of time.
def gen_points_faiss(
    n_pts: int, min_val: float, max_val: float, dist: float, n_batch: int = 100
):
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
    nlist = 100  # Clusters
    quantizer = faiss.IndexFlatL2(dim)
    index = faiss.IndexIVFFlat(quantizer, dim, nlist)
    training_data = np.random.uniform(min_val, max_val, size=(3900, 3)).astype(
        "float32"
    )
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
            D, Idx = index.search(batch, 1)
            valid = np.sqrt(D[:, 0]) >= dist  # Check distances
            valid_points = batch[valid]
        else:
            valid_points = batch

        index.add(valid_points)
        pts.extend(valid_points)
        i += valid_points.shape[0]

    return np.array(pts[:n_pts])


start = time.time()
# https://en.wikipedia.org/wiki/Log-normal_distribution
# Generate each radius to be used for the spheres
sigma_o = np.sqrt(np.log(1 + (R_OS / R_OM) ** 2))
mu_o = np.log(R_OM) - sigma_o**2 / 2

R_outer = []
sum_vol = 0
tgt = (L**3) * VOL_FR
while sum_vol < tgt:
    r = np.random.lognormal(mu_o, sigma_o)
    vol = (4 / 3) * np.pi * (r**3)
    if sum_vol + vol > tgt:
        break
    sum_vol += (4 / 3) * np.pi * (r**3)
    R_outer.append(r)
R_outer = np.array(R_outer)

# Every sphere has one inner and one outer radius
N = R_outer.shape[0]  # Number of spheres
sigma_i = np.sqrt(np.log(1 + (R_IS / R_IM) ** 2))
mu_i = np.log(R_IM) - sigma_i**2 / 2
R_inner = np.random.lognormal(mu_i, sigma_i, N)


max_r = np.max(R_outer)
# Each point must be a diameter away.
# Each point must be within [-L/2 + max(R), L/2 - max(R)]^3
centers = gen_points_faiss(N, -L / 2 + max_r, L / 2 - max_r, 2 * max_r)
core_pts = []
shell_pts = []
for i in range(N):
    core = Ellipsoid(D1, R_inner[i])
    c = core.make_obj() + centers[i]
    for p in c:
        core_pts.append(p)
    shell = Ellipsoid(D2, R_outer[i], R_inner[i])
    s = shell.make_obj() + centers[i]
    for p in s:
        shell_pts.append(p)
core_pts = np.array(core_pts)
shell_pts = np.array(shell_pts)

print("TIME (sec)", time.time() - start)

append = "faiss"
save_coords(core_pts, f"out/core_out_{append}.txt")
save_coords(shell_pts, f"out/shell_out_{append}.txt")

# fig = plt.figure()
# ax = fig.add_subplot(111, projection="3d")
#
# # Scatter plot the data
# ax.scatter(shell_pts[:, 0], shell_pts[:, 1], shell_pts[:, 2])
#
#
# # Save the plot as an image
# plt.savefig("core.png")
