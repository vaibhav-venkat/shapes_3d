import numpy as np
from ..modules.onion import Onion
from pathlib import Path
from ..modules.utils import save_dump, make_centers

thickness_mean = np.array([10.0, 7.0, 6.0, 5.0, 4.0])
thickness_std = np.array([1.5, 1.2, 0.5, 0.8, 1.0])
density = np.array([0.0, 0.05, 0.1, 0.03, 0.2])
box_length: float = 800
volume_fraction: float = 0.05
assert density.shape == thickness_std.shape == thickness_mean.shape

list_radii: list = []
target_vol: float = (box_length**3) * volume_fraction
total_vol: float = 0
log_thickness_std: np.ndarray = np.sqrt(
    np.log(1 + (thickness_std / thickness_mean) ** 2)
)
log_thickness_std: np.ndarray = np.log(thickness_mean) - log_thickness_std**2 / 2
while total_vol < target_vol:
    total_radius: float = 0
    current_shell = np.random.lognormal(log_thickness_std, log_thickness_std)
    total_vol += float(np.sum(current_shell) ** 3) * np.pi * 4 / 3
    if total_vol > target_vol:
        break
    list_radii.append(current_shell)
radii: np.ndarray = np.array(list_radii)
num_pts: int = radii.shape[0]


max_total_radius: float = np.max(radii.sum(axis=1))
centers = make_centers(
    num_pts,
    -box_length / 2 + max_total_radius,
    box_length / 2 - max_total_radius,
    2 * max_total_radius,
)
points = []
for i in range(num_pts):
    if (i + 1) % 100 == 0 or i == 0 or i == num_pts - 1:
        print("N =", i + 1, "out of", num_pts)
    shell = Onion(radii[i], centers[i], density)
    points.extend(shell.pts)
points = np.array(points)


def save_coords(points: np.ndarray, filename: str = "out.txt") -> None:
    """
    Save coordinates to a file
    """
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(filename, points, fmt="%.6f", header="X Y Z shell", comments="")
    print("saved to", filename)


save_coords(points, "out/onion.txt")
save_dump([points], "out/onion.dump", box_length)
