import numpy as np
from ..modules.ellipsoid import Ellipsoid
from ..modules.utils import save_dump, make_centers_iter

box_length = 1000
outer_radius_mean = 30.0
outer_radius_std = 5.0
inner_radius_mean = 20.0
inner_radius_std = 3.0
volume_fraction = 0.05
core_density = 0.1
shell_density = 0.05

thickness_mean = outer_radius_mean - inner_radius_mean
thickness_std = np.sqrt(outer_radius_std**2 - inner_radius_std**2)


def save_coords(points, filename="out.txt"):
    """
    Save coordinates to a file
    """
    np.savetxt(filename, points, fmt="%.4f")


log_std_thickness = np.sqrt(np.log(1 + (thickness_std / thickness_mean) ** 2))
log_mean_thickness = np.log(thickness_mean) - log_std_thickness**2 / 2
log_std_core = np.sqrt(np.log(1 + (inner_radius_std / inner_radius_mean) ** 2))
lgo_mean_core = np.log(inner_radius_mean) - log_std_core**2 / 2
R_outer = []
R_inner = []
total_volume = 0
target = (box_length**3) * volume_fraction
while total_volume < target:
    thickness = np.random.lognormal(log_mean_thickness, log_std_thickness)
    inner_radius = np.random.lognormal(lgo_mean_core, log_std_core)
    outer_radius = thickness + inner_radius
    volume = (4 / 3) * np.pi * ((outer_radius**3))
    if total_volume + volume > target:
        break
    total_volume += volume
    R_outer.append(outer_radius)
    R_inner.append(inner_radius)
R_outer = np.array(R_outer)
R_inner = np.array(R_inner)
num_pts = R_outer.shape[0]

dist: np.ndarray = R_outer
print("particles:", num_pts)
centers: np.ndarray = make_centers_iter(num_pts, -box_length / 2, box_length / 2, dist)
core_points = []
shell_points = []
for i in range(num_pts):
    core = Ellipsoid(core_density, R_inner[i])
    core_shift = core.make_obj() + centers[i]
    for point in core_shift:
        core_points.append(point)
    shell = Ellipsoid(shell_density, R_outer[i], R_inner[i])
    shell_shift = shell.make_obj() + centers[i]
    for point in shell_shift:
        shell_points.append(point)
core_points = np.array(core_points)
shell_points = np.array(shell_points)

save_coords(core_points, "out/cube_sphere_core.txt")
save_coords(shell_points, "out/cube_sphere_shell.txt")
save_dump([core_points, shell_points], "out/cube_spheres.dump", box_length)
