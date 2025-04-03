import numpy as np
from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import save_dump, make_centers

box_length = 1000
axis_length_mean: np.ndarray = np.array([30, 50, 65])
axis_length_std: np.ndarray = np.array([5, 6, 3])
volume_fraction = 0.05
density = 0.02

log_std_axis: np.ndarray = np.sqrt(
    np.log(1 + (axis_length_std / axis_length_mean) ** 2)
)
log_mean_axis: np.ndarray = np.log(axis_length_mean) - log_std_axis**2 / 2
axis_lengths_list: list = []
total_volume = 0
target = (box_length**3) * volume_fraction
while total_volume < target:
    x_length = np.random.lognormal(log_mean_axis[0], log_std_axis[0])
    y_length = np.random.lognormal(log_mean_axis[1], log_std_axis[1])
    z_length = np.random.lognormal(log_mean_axis[2], log_std_axis[2])
    volume = (4 / 3) * np.pi * (x_length * y_length * z_length)
    if total_volume + volume > target:
        break
    total_volume += volume
    axis_lengths_list.append([x_length, y_length, z_length])
axis_length: np.ndarray = np.array(axis_lengths_list)

num_pts = axis_length.shape[0]

max_r = np.amax(axis_length)
print("particles:", num_pts)
centers = make_centers(
    num_pts, -box_length / 2 + max_r, box_length / 2 - max_r, 2 * max_r
)
points: list = []
for i in range(num_pts):
    ellipsoid: Ellipsoid = Ellipsoid(
        density,
        x_outer_radius=axis_length[i][0],
        y_outer_radius=axis_length[i][1],
        z_outer_radius=axis_length[i][2],
    )
    shifted_ellipsoid = ellipsoid.make_obj() + centers[i]
    for point in shifted_ellipsoid:
        points.append(point)
final_points: np.ndarray = np.array(points)
save_dump([final_points], "out/ellipsoid_box.dump", box_length)
